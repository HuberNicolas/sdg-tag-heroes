import os
import time

import joblib
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker

from settings.settings import ReducerSettings, LoaderSettings, EmbeddingsSettings
from datetime import datetime
from itertools import product  # For generating parameter combinations
from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qclient
from models.publications.dimensionality_reduction import DimensionalityReduction
from models.sdg_prediction import SDGPrediction
from models.publications.publication import Publication
import umap
import numpy as np

reducer_settings = ReducerSettings()
loader_settings = LoaderSettings()
embeddings_settings = EmbeddingsSettings()

# Initialize session
Session = sessionmaker(bind=mariadb_engine)



def generate_umap_params():
    """Generate a dictionary of UMAP parameter combinations."""
    param_combinations = list(
        product(
            reducer_settings.UMAP_N_NEIGHBORS_ARRAY,
            reducer_settings.UMAP_MIN_DIST_ARRAY,
            reducer_settings.UMAP_N_COMPONENTS_ARRAY
        )
    )
    umap_params = {
        idx + 1: {
            'n_neighbors': combination[0],
            'min_dist': combination[1],
            'n_components': combination[2],
        }
        for idx, combination in enumerate(param_combinations)
    }
    return umap_params

def create_dimensionality_reductions():
    sdg_columns = [f"sdg{i}" for i in range(1, 18)]  # SDG1 to SDG17
    current_timestamp = datetime.now()

    # Dynamically generate UMAP parameters from settings
    umap_params = generate_umap_params()
    print(umap_params)

    with Session() as session:
        for sdg_index, sdg_column in enumerate(sdg_columns, start=1):
            print(f"Processing SDG{sdg_index}...")

            level = 1  # Start level numbering at 1 for each SDG

            for range_index, (upper, lower) in enumerate(reducer_settings.FILTER_RANGES, start=1):
                print(f"  Applying filter range {upper} - {lower}... - Level {level}")

                start = time.time()
                # Query publications based on SDG filter
                publications = (
                    session.query(Publication)
                    .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
                    .filter(
                        SDGPrediction.prediction_model == "Aurora",
                        getattr(SDGPrediction, sdg_column) <= upper,
                        getattr(SDGPrediction, sdg_column) > lower,
                    )
                    .order_by(desc(getattr(SDGPrediction, sdg_column)))
                    # .limit(1000)
                    .all()
                )
                end = time.time()

                print(f"  Found {len(publications)} publications for SDG{sdg_index} in range {upper} - {lower}. Took {end - start} seconds.")

                if not publications:
                    continue  # Skip if no publications for this SDG and range

                # Fetch embeddings from Qdrant
                embeddings_data = fetch_embeddings_from_qdrant(publications)

                if not embeddings_data:
                    print(f"  Failed to fetch embeddings for SDG{sdg_index} in range {upper} - {lower}.")
                    continue

                # Map SQL IDs to embeddings
                sql_id_to_embedding = {item['sql_id']: item['content'] for item in embeddings_data}

                # Filter publications with valid embeddings
                filtered_publications = [
                    pub for pub in publications if pub.publication_id in sql_id_to_embedding
                ]

                # Prepare ordered embeddings
                ordered_embeddings = [
                    sql_id_to_embedding[pub.publication_id] for pub in filtered_publications
                ]

                if not ordered_embeddings:
                    print(f"  No matching embeddings found for SDG{sdg_index} in range {upper} - {lower}.")
                    continue

                # Initialize container for dimensionality reductions
                data_to_insert = []

                for params in umap_params.values():  # Iterate over UMAP parameter sets
                    print(f"    Performing umap on {params['n_neighbors']} neighbors of {params['min_dist']}...")

                    # Perform UMAP reduction
                    reducer = umap.UMAP(
                        n_neighbors=params['n_neighbors'],
                        min_dist=params['min_dist'],
                        n_components=params['n_components'],
                        random_state=31011997,
                        n_jobs = 1  # Explicitly disable parallelism
                    )
                    start = time.time()
                    umap_result = reducer.fit_transform(ordered_embeddings)
                    end = time.time()
                    print(f"UMAP fit took {end - start} seconds.")

                    model_dir = f"./data/api/umap_model/config_{params['n_neighbors']}_{params['min_dist']}_{params['n_components']}"
                    os.makedirs(model_dir, exist_ok=True)
                    model_path = os.path.join(model_dir, f"SDG{sdg_index}.joblib")

                    # Save the UMAP model
                    joblib.dump(reducer, model_path)
                    print(f"UMAP model saved to {model_path}.")

                    for pub, coords in zip(filtered_publications, umap_result):
                        x_coord, y_coord = coords.tolist()

                        reduction_details = (
                            f"UMAP with n_neighbors={params['n_neighbors']}, min_dist={params['min_dist']}, "
                            f"n_components={params['n_components']}, filter_range={upper}-{lower}"
                        )
                        reduction_shorthand = (
                            f"UMAP-{params['n_neighbors']}-{params['min_dist']}-{params['n_components']}"
                        )

                        dim_red = DimensionalityReduction(
                            publication_id=pub.publication_id,
                            reduction_technique="UMAP",
                            reduction_details=reduction_details,
                            reduction_shorthand=reduction_shorthand,
                            x_coord=x_coord,
                            y_coord=y_coord,
                            z_coord=0.0,  # Assuming 2D UMAP
                            sdg=sdg_index,
                            level=level,  # Use the current level
                            created_at=current_timestamp,
                            updated_at=current_timestamp,
                        )
                        data_to_insert.append(dim_red)

                    session.add_all(data_to_insert)
                    session.commit()
                    print(f"    Committed {len(data_to_insert)} dimensionality reductions.")
                    data_to_insert = []


                # Only increment the level after all insertions for the current filter range
                level += 1


def fetch_embeddings_from_qdrant(publications):


    # Extract publication IDs (oai_identifier_num) from the publications
    publication_ids = [int(pub.oai_identifier_num) for pub in publications]

    try:
        start = time.time()
        # Fetch embeddings using the list of publication IDs
        results = qclient.retrieve(
            collection_name=loader_settings.PUBLICATIONS_COLLECTION_NAME,
            ids=publication_ids,
            with_vectors=True,
            with_payload=True,
        )
        end = time.time()
        print(f"Retrieved {len(publication_ids)} publications in {end - start} seconds.")

        # Extract embeddings and SQL IDs
        embeddings = [
            {'sql_id': result.payload['sql_id'], 'content': result.vector['content']}
            for result in results
        ]

        # Debug: Log the number of embeddings retrieved
        print(f"Successfully retrieved {len(embeddings)} embeddings.")
        return embeddings  # Return structured embeddings for further processing

    except Exception as e:

        print(f"Failed to fetch embeddings from Qdrant: {e}")
        # Return an empty list in case of failure
        return []


# Call the function
create_dimensionality_reductions()

import json

import pandas as pd
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from models.publications.publication import Publication
from models.publications.dimensionality_reduction import DimensionalityReduction
from models.collection import Collection
from db.mariadb_connector import engine

# Initialize session
Session = sessionmaker(bind=engine)

# Paths to CSV files
TOPIC_INFO_PATH = "./data/pipeline/collections/wwf_topic_info_simplified.csv"
TOPIC_DATA_PATH = "./data/pipeline/collections/wwf_topic_data.csv"

BATCH_SIZE = 1000  # Process entities in batches

WWF_TOPIC_ID_OFFSET = 1000

def create_collections_and_reductions():
    """
    Create Collection and DimensionalityReduction entities from the provided CSV files
    and link them to existing publications in batches.
    """
    with Session() as session:
        # Step 1: Process topic_info.csv and create Collection entities
        topic_info_df = pd.read_csv(TOPIC_INFO_PATH)

        # Clean column names to avoid KeyError due to extra spaces or mismatched names
        topic_info_df.columns = topic_info_df.columns.str.strip()

        collections_to_add = [
            Collection(
                topic_id=int(row["Topic"]) + WWF_TOPIC_ID_OFFSET,  # Unique topic_id
                count=int(row["Count"]),
                name=row["Name"].strip(),
                short_name=row["GPT_Name"].strip(),
                representation=json.dumps(eval(row["Representation"].strip())),
                aspect1=json.dumps(eval(row["Aspect1"].strip())),
                aspect2=json.dumps(eval(row["Aspect2"].strip())),
                aspect3=json.dumps(eval(row["Aspect3"].strip())),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for _, row in topic_info_df.iterrows()
        ]

        session.bulk_save_objects(collections_to_add)
        session.commit()
        print("Collections created successfully.")

        # Load collections from the database for linking
        existing_collections = session.query(Collection).all()
        topic_id_to_collection_id = {col.topic_id: col.collection_id for col in existing_collections}

        # Step 2: Process topic_data.csv and create DimensionalityReduction entities in batches
        topic_data_df = pd.read_csv(TOPIC_DATA_PATH)
        topic_data_df.columns = topic_data_df.columns.str.strip()

        # Convert `id` column to integers directly
        publication_ids = topic_data_df["id"].astype(int)

        existing_publications = session.query(Publication).filter(Publication.publication_id.in_(publication_ids)).all()
        pub_id_map = {pub.publication_id: pub for pub in existing_publications}

        reductions_to_add = []
        for idx, row in topic_data_df.iterrows():
            pub_id = int(row["id"])
            publication = pub_id_map.get(pub_id)

            if not publication:
                print(f"Publication with ID {pub_id} not found, skipping.")
                continue

            # Link publication with collection based on topic_id
            topic_id = int(row["topic"])  # Assuming 'topic' column corresponds to the collection's topic_id
            collection_id = topic_id_to_collection_id.get(topic_id)

            if collection_id:
                publication.collection_id = collection_id  # Link the publication to the collection

            # From BertTopic Pipeline
            # dim_reduction_params = {"n_neighbors": 10, "n_components": 2, "min_dist": 0.0, "metric": "cosine"},
            # cluster_method_params = {"min_cluster_size": 30, "metric": "euclidean", "prediction_data": True},

            reduction_details = (
                f"TM for WWF subset using UMAP with n_neighbors=10, min_dist=0.0, n_components=2, metric=cosine"
            )
            reduction_shorthand = "TM-WWF-UMAP-10-0.0-2"

            dim_reduction = DimensionalityReduction(
                publication_id=publication.publication_id,
                reduction_technique="UMAP",
                reduction_details=reduction_details,
                reduction_shorthand=reduction_shorthand,
                x_coord=float(row["x"]),
                y_coord=float(row["y"]),
                z_coord=0.0,  # Assuming 2D reductions
                sdg=0,  # Set SDG to 0
                level=0,  # Default level for these reductions
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            reductions_to_add.append(dim_reduction)

            # Commit in batches
            if len(reductions_to_add) >= BATCH_SIZE:
                session.bulk_save_objects(reductions_to_add)
                session.commit()
                print(f"Committed {len(reductions_to_add)} dimensionality reductions.")
                reductions_to_add = []

        # Commit any remaining reductions
        if reductions_to_add:
            session.bulk_save_objects(reductions_to_add)
            session.commit()
            print(f"Committed the remaining {len(reductions_to_add)} dimensionality reductions.")

if __name__ == "__main__":
    create_collections_and_reductions()

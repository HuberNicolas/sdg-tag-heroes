import argparse
import gc
import os
import umap
from qdrant_client import QdrantClient
from db.qdrantdb_connector import client as qdrantdb_client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from models.base import Base
from models.author import Author
from models.division import Division
from models.faculty import Faculty
from models.institute import Institute
from models.sdg_prediction import SDGPrediction
from models.sdg_label import SDGLabel
from models.sdg_label_history import SDGLabelHistory
from models.sdg_label_decision import SDGLabelDecision
from models.sdg_user_label import SDGUserLabel
from models.dim_red import DimRed
from models.publication import Publication
from models.user import User
from models.admin import Admin
from models.expert import Expert
from models.labeler import Labeler


from settings.settings import ReducerSettings, LoaderSettings, EmbeddingsSettings
reducer_settings = ReducerSettings()
loader_settings = LoaderSettings()
embeddings_settings = EmbeddingsSettings()

# Setup Logging
from utils.logger import logger
logging = logger(reducer_settings.REDUCER_LOG_NAME)

class UmapProcessor:
    def __init__(self, qdrantdb_client, mariadb_batch_size=100):
        self.qclient = qdrantdb_client
        self.mariadb_batch_size = mariadb_batch_size


    def fetch_embeddings_from_qdrant(self, publications):
        """Fetch embeddings from Qdrant."""
        logging.info(
            f"Fetching embeddings from Qdrant for {len(publications)} publications..."
        )

        # Extract publication IDs (oai_identifier_num) from the publications
        publication_ids = [int(pub.oai_identifier_num) for pub in publications]

        try:
            # Fetch embeddings using the list of publication IDs
            results = self.qclient.retrieve(
                collection_name=loader_settings.PUBLICATIONS_COLLECTION_NAME, ids=publication_ids
            )

            # TODO: fix

            # Extract embeddings from the results
            embeddings = [result.vector[embeddings_settings.VECTOR_CONTENT_NAME] for result in results]

            return embeddings

        except Exception as e:
            logging.error(f"Failed to fetch embeddings from Qdrant: {e}")
            return [[0.0] * embeddings_settings.VECTOR_SIZE] * len(
                publications
            )  # Return default zero embeddings in case of failure

    def perform_umap(self, embeddings, n_neighbors=ReducerSettings.UMAP_N_NEIGHBORS, min_dist=ReducerSettings.UMAP_MIN_DIST, n_components=ReducerSettings.UMAP_N_COMPONENTS):
        """Perform UMAP dimensionality reduction on the provided embeddings."""
        logging.info("Starting UMAP dimensionality reduction...")
        reducer = umap.UMAP(
            n_neighbors=n_neighbors, min_dist=min_dist, n_components=n_components
        )
        umap_result = reducer.fit_transform(embeddings)
        logging.info("UMAP dimensionality reduction completed.")
        return umap_result


    def upload_umap_results(self, publications, umap_results, session):
        """Upload UMAP-reduced coordinates to the database and mark them as reduced in batches."""
        try:
            batch_counter = 0  # Counter for the batch
            for i, (pub, umap_coords) in enumerate(zip(publications, umap_results)):
                # Convert numpy.float32 to Python float
                umap_x, umap_y = map(float, umap_coords)

                reduction_details_string = f"n_neighbors={ReducerSettings.UMAP_N_NEIGHBORS}, min_dist={ReducerSettings.UMAP_MIN_DIST}, n_components={ReducerSettings.UMAP_N_COMPONENTS}"

                reduction_shorthand_string = f"UMAP-xy-{ReducerSettings.UMAP_N_NEIGHBORS}-{ReducerSettings.UMAP_MIN_DIST}-{ReducerSettings.UMAP_N_COMPONENTS}"

                dim_red_entry = DimRed(
                    publication_id=pub.publication_id,
                    reduction_technique="UMAP",
                    reduction_details=reduction_details_string,
                    reduction_shorthand=reduction_shorthand_string,
                    x_coord=umap_x,
                    y_coord=umap_y,
                    z_coord=0
                )

                # Add the UMAP result to the publication
                session.add(dim_red_entry)
                pub.dimreduced = True

                batch_counter += 1

                # Commit the batch after processing `mariadb_batch_size` publications
                if batch_counter >= self.mariadb_batch_size:
                    session.commit()
                    logging.info(f"Committed batch of {self.mariadb_batch_size} publications.")
                    batch_counter = 0  # Reset counter for the next batch

            # Commit any remaining publications that were not part of a full batch
            if batch_counter > 0:
                session.commit()
                logging.info(f"Committed remaining {batch_counter} publications.")

            logging.info(
                f"Successfully saved UMAP results for {len(publications)} publications."
            )
        except Exception as e:
            session.rollback()  # Rollback on failure
            logging.error(f"Failed to upload UMAP results: {e}")
            raise  # Re-raise the exception after rollback to handle externally


    def process_and_reduce(self, session):
        """Process un-UMAPed publications and reduce their embeddings using UMAP."""
        logging.info("Starting the UMAP reduction process...")

        try:
            # Fetch publications that haven't been UMAP-reduced yet
            publications = (
                session.query(Publication).filter_by(dimreduced=False).all()
            )

            if not publications:
                logging.info("No more publications to reduce.")

            logging.info(
                f"Processing {len(publications)} publications for UMAP reduction..."
            )

            # Fetch embeddings from Qdrant
            embeddings = self.fetch_embeddings_from_qdrant(publications)

            # Perform UMAP reduction
            umap_results = self.perform_umap(embeddings)

            # Upload the UMAP-reduced results to the database
            self.upload_umap_results(publications, umap_results, session)

        except Exception as e:
            logging.error(f"Error during UMAP processing: {e}")



def setup_sqlite_connection():
    """Setup SQLite database connection."""
    db_url = "sqlite:///publications.db"
    engine = create_engine(db_url, echo=True)
    return engine


def main(db, mariadb_batch_size):
    logging.info("Starting Reducer loader...")

    try:
        # Determine the database engine based on db_type (sqlite or mariadb)
        if db == "mariadb":
            from db.mariadb_connector import engine as mariadb_engine  # MariaDB engine

            engine = mariadb_engine
            logging.info("Using MariaDB engine.")
        else:
            engine = setup_sqlite_connection()
            logging.info("Using SQLite engine.")

        # Setup database session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Ensure tables are created
        Base.metadata.create_all(engine)

        # Initialize UMAP processor
        #umap_processor = UmapProcessor(qdrantdb_client, mariadb_batch_size=mariadb_batch_size)

        # Process and reduce un-UMAPed publications
        #umap_processor.process_and_reduce(session)

    except Exception as e:
        logging.error(f"Failed to start the UMAP-Qdrant loader: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the UMAP-Qdrant loader with SQLite or MariaDB."
    )
    parser.add_argument(
        "--db",
        choices=["sqlite", "mariadb"],
        default="sqlite",
        help="Specify the database to use: sqlite or mariadb (default: sqlite).",
    )
    parser.add_argument(
        "--mariadb_batch_size",
        type=int,
        default=reducer_settings.DEFAULT_MARIADB_BATCH_SIZE,
        help=f"Specify the batch size for uploading (default: {reducer_settings.DEFAULT_MARIADB_BATCH_SIZE}).",
    )

    args = parser.parse_args()

    main(args.db, args.mariadb_batch_size)

def reducer_main(db, mariadb_batch_size):
    main(db, mariadb_batch_size)

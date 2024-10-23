import argparse
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from sqlalchemy.orm import sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrantdb_client

from pipeline.zora.embeddings import PublicationEmbeddingGenerator



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

# Ensure these settings are properly initialized
from settings.settings import EmbeddingsSettings, SDGSettings, LoaderSettings
embeddings_settings = EmbeddingsSettings()
sdg_settings = SDGSettings()
loader_settings = LoaderSettings()

# Setup Logging
from utils.logger import logger
logging = logger(loader_settings.LOADER_LOG_NAME)

class QdrantUploader:
    def __init__(self, qdrantdb_client):
        self.qclient = qdrantdb_client
        logging.info(f"Initialized QdrantUploader with client: {self.qclient}")

    def fetch_goal_predictions(self, publications, session):
        """Fetch SDG predictions for a list of publications."""
        goal_predictions = {}
        for pub in publications:
            sdg_preds = (
                session.query(SDGPrediction)
                .filter_by(publication_id=pub.publication_id)
                .all()
            )
            if sdg_preds:
                for sdg_pred in sdg_preds:
                    model_name = sdg_pred.prediction_model.lower()
                    predictions = [
                        sdg_pred.sdg1, sdg_pred.sdg2, sdg_pred.sdg3, sdg_pred.sdg4,
                        sdg_pred.sdg5, sdg_pred.sdg6, sdg_pred.sdg7, sdg_pred.sdg8,
                        sdg_pred.sdg9, sdg_pred.sdg10, sdg_pred.sdg11, sdg_pred.sdg12,
                        sdg_pred.sdg13, sdg_pred.sdg14, sdg_pred.sdg15, sdg_pred.sdg16,
                        sdg_pred.sdg17,
                    ]
                    if pub.publication_id not in goal_predictions:
                        goal_predictions[pub.publication_id] = {}
                    goal_predictions[pub.publication_id][f"goal_{model_name}"] = predictions
                logging.info(f"SDG predictions for publication ID {pub.publication_id}: {goal_predictions[pub.publication_id]}")
            else:
                goal_predictions[pub.publication_id] = {"goal_default": [0.0] * sdg_settings.SDGOAL_NUMBER}
                logging.warning(f"No SDG predictions found for publication ID {pub.publication_id}. Defaulting to zeros.")

        return goal_predictions

    def upload_batch(self, publications, embeddings, goal_predictions, session):
        """Upload a batch of embeddings and predictions to Qdrant."""
        logging.info(f"Uploading a batch of {len(publications)} publications to Qdrant...")
        try:
            points = []
            for pub, emb in zip(publications, embeddings):
                vectors = {"content": emb.tolist()}
                vectors.update(goal_predictions.get(pub.publication_id, {"goal_default": [0.0] * sdg_settings.SDGOAL_NUMBER}))

                points.append(
                    PointStruct(
                        id=int(pub.oai_identifier_num),
                        vector=vectors,
                        payload={
                            "sql_id": pub.publication_id,
                            "oai_identifier": pub.oai_identifier,
                            "oai_identifier_num": pub.oai_identifier_num,
                            "title": pub.title,
                            "description": pub.description,
                        },
                    )
                )

            # Upload points to Qdrant
            self.qclient.upload_points(collection_name=loader_settings.PUBLICATIONS_COLLECTION_NAME, points=points)
            logging.info(f"Successfully uploaded {len(publications)} publications to Qdrant.")

            # Mark publications as embedded in the database
            for pub in publications:
                pub.embedded = True
                session.commit()

        except Exception as e:
            logging.error(f"Failed to upload batch to Qdrant: {e}")
            raise

    def init_collection(self, collection_name=loader_settings.PUBLICATIONS_COLLECTION_NAME):
        """Initialize the Qdrant collection if it doesn't exist."""
        logging.info(f"Creating or recreating collection {collection_name} in Qdrant...")
        try:
            if not self.qclient.collection_exists(collection_name=collection_name):
                self.qclient.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "content": VectorParams(size=embeddings_settings.VECTOR_SIZE, distance=Distance.DOT),
                        "goal_zora": VectorParams(size=sdg_settings.SDGOAL_NUMBER, distance=Distance.DOT),
                        "goal_dvdblk": VectorParams(size=sdg_settings.SDGOAL_NUMBER, distance=Distance.DOT),
                    },
                )
                logging.info(f"Collection {collection_name} successfully created.")
            else:
                logging.info(f"Collection {collection_name} already exists.")
        except Exception as e:
            logging.error(f"Failed to create collection {collection_name}: {e}")
            raise

    def process_and_upload(self, embedding_generator, session, batch_size):
        """Process unembedded publications and upload them to Qdrant."""
        logging.info("Starting the embedding generation and upload process...")

        while True:
            try:
                # Fetch unprocessed publications
                publications = (
                    session.query(Publication)
                    .join(SDGPrediction)
                    .filter(Publication.embedded == False)
                    .filter(SDGPrediction.predicted == True)
                    .limit(batch_size)
                    .all()
                )

                if not publications:
                    logging.info("No new publications to embed. Waiting for more data...")
                    break

                # Generate embeddings for the publications
                logging.info(f"Generating embeddings for {len(publications)} publications...")
                embeddings = embedding_generator.encode_publications(publications)

                # Fetch SDG predictions from the database
                logging.info(f"Fetching SDG predictions for {len(publications)} publications...")
                goal_predictions = self.fetch_goal_predictions(publications, session)

                # Upload the batch of embeddings and predictions
                self.upload_batch(publications, embeddings, goal_predictions, session)

            except Exception as e:
                logging.error(f"Error during processing and uploading: {e}")
                break

def main(db, batch_size):
    logging.info("Starting main Qdrant loader...")

    try:
        # Determine the database engine based on db_type (sqlite or mariadb)
        if db == "mariadb":
            # Use the MariaDB engine from the `db.mariadb_connector`
            engine = mariadb_engine
            logging.info("Using MariaDB engine.")
        else:
            # Fallback to SQLite engine
            from sqlalchemy import create_engine

            engine = create_engine("sqlite:///publications.db")
            logging.info("Using SQLite engine.")

        # Initialize embedding generator and Qdrant uploader
        # Make sure that in settings the correct cuda device is selected!
        embedding_generator = PublicationEmbeddingGenerator(engine, batch_size)
        uploader = QdrantUploader(qdrantdb_client)
        # Create collection in Qdrant
        uploader.init_collection()

        # Setup database session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Continuously process and upload unprocessed publications
        uploader.process_and_upload(embedding_generator, session, batch_size)

    except Exception as e:
        logging.error(f"Failed to start the Qdrant loader: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Qdrant loader with SQLite or MariaDB.")
    parser.add_argument("--db", choices=["sqlite", "mariadb"], default="sqlite", help="Specify the database to use: sqlite or mariadb (default: sqlite).")
    parser.add_argument("--batch_size", type=int, default=loader_settings.DEFAULT_BATCH_SIZE, help=f"Specify the batch size for embedding generation and uploading (default: {loader_settings.DEFAULT_BATCH_SIZE}).")

    args = parser.parse_args()
    main(args.db, args.batch_size)

def loader_main(db, batch_size):
    main(db, batch_size)

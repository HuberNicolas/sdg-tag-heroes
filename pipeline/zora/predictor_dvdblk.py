"""
Predict SDG goals with the SciBERT model "dvdblk/scibert_sdg_cased_zo-up" (see utils/sdg_predictor.py)
and store them as SDGPrediction rows with prediction_model="Dvdblk".

This is an alternative to the Aurora predictor (predictor.py).
"""
import argparse
import gc

import torch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.sdg_predictor import sdg_predictor

from models import Publication, SDGPrediction

from settings.settings import PredictionSettings
predictor_settings = PredictionSettings()

#os.environ[PredictionSettings.CUDA_VISIBLE_DEVICES_KEY] = PredictionSettings.CUDA_VISIBLE_DEVICES_VALUE

# Setup Logging
from utils.logger import logger
logging = logger(predictor_settings.DVDBLK_PREDICTOR_LOG_NAME)




def update_sdg_field(prediction_entry, predictions, precision=8):
    """Dynamically update all relevant SDG fields for a prediction entry, rounding the value to a specified precision."""
    for i in range(1, 18):
        rounded_prediction = round(predictions[i - 1], precision)
        setattr(prediction_entry, f'sdg{i}', rounded_prediction)  # Set sdg1 to sdg17

def process_and_predict_in_stages(session, batch_size, mariadb_batch_size):
    """
    Perform staged prediction by loading one model at a time, predicting across all publications,
    and saving results in batches.
    """
    logging.info("Starting the staged prediction process...")

    # Fetch all publications that have no Dvdblk prediction yet
    publications = (
        session.query(Publication)
        .filter(~Publication.sdg_predictions.any(SDGPrediction.prediction_model == "Dvdblk"))
        .all()
    )

    if not publications:
        logging.info("No publications to predict. Process complete.")
        return

    # Generate predictions for all publications
    predictions = []
    for i in range(0, len(publications), batch_size):
        batch = publications[i: i + batch_size]

        # TODO: Add to settings for simpler config
        abstracts = [f"{pub.title}\n{pub.description}" for pub in batch]
        batch_predictions = [sdg_predictor(abstract) for abstract in abstracts]
        predictions.extend(batch_predictions)


    # Process predictions in batches for uploading
    for i in range(0, len(publications), mariadb_batch_size):
        batch = publications[i: i + mariadb_batch_size]
        batch_predictions = predictions[i: i + mariadb_batch_size]

        logging.info(
            f"Processing batch {i // mariadb_batch_size + 1} (Publication IDs {batch[0].publication_id} to {batch[-1].publication_id})"
        )

        # Collect all prediction entries to update in a batch
        updated_entries = []
        for pub, prediction in zip(batch, batch_predictions):
            prediction_entry = SDGPrediction(
                publication_id=pub.publication_id,
                prediction_model="Dvdblk",
            )
            # Convert to list
            prediction_list = prediction.detach().numpy().tolist()[0]

            update_sdg_field(prediction_entry, prediction_list)
            prediction_entry.last_predicted_goal = 17
            prediction_entry.predicted = True

            # Add to the list of updated entries
            updated_entries.append(prediction_entry)


        # Perform bulk update
        if updated_entries:
            session.bulk_save_objects(updated_entries)
            try:
                session.commit()
                logging.info(
                    f"Batch {i // mariadb_batch_size + 1} predictions for model Dvdblk saved."
                )
            except Exception as e:
                logging.error(f"Error committing batch {i // mariadb_batch_size + 1}: {e}")
                session.rollback()  # Rollback on error

        # Clear memory
        del batch, batch_predictions
        gc.collect()


    # Clear memory
    del predictions
    gc.collect()

    logging.info("All predictions complete.")


def setup_sqlite_connection():
    """Setup SQLite database connection."""
    db_url = "sqlite:///publications.db"
    engine = create_engine(db_url)
    return engine


def reset_database(session):
    """Reset the SDGPrediction table by deleting all records."""
    session.query(SDGPrediction).delete()
    session.commit()
    logging.info("Database reset complete.")

def main(db, batch_size, mariadb_batch_size):
    logging.info("Starting Predictor...")

    logging.info(f"GPU available: {torch.cuda.is_available()}")

    # Configure database connection based on argument
    if db == "mariadb":
        from db.mariadb_connector import (
            engine as mariadb_engine,  # Use the mariadb connector
        )

        session_maker = sessionmaker(bind=mariadb_engine)
        logging.info("Using MariaDB database.")
    else:
        sqlite_engine = setup_sqlite_connection()
        session_maker = sessionmaker(bind=sqlite_engine)
        logging.info("Using SQLite database.")

    session = session_maker()

    # Start the staged prediction process
    logging.info("Starting the batch prediction process.")
    process_and_predict_in_stages(session, batch_size=batch_size, mariadb_batch_size=mariadb_batch_size)

    # Close session
    session.close()
    logging.info("Batch prediction process complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run SDG batch predictor with SQLite or MariaDB."
    )
    parser.add_argument(
        "--db",
        choices=["sqlite", "mariadb"],
        default="sqlite",
        help="Specify the database to use: sqlite or mariadb (default: sqlite)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=predictor_settings.DEFAULT_BATCH_SIZE,
        help=f"Specify the batch size for prediction (default: {predictor_settings.DEFAULT_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--mariadb_batch_size",
        type=int,
        default=predictor_settings.DEFAULT_MARIADB_BATCH_SIZE,
        help=f"Specify the batch size for uploading (default: {predictor_settings.DEFAULT_MARIADB_BATCH_SIZE}).",
    )
    args = parser.parse_args()
    main(args.db, args.batch_size, args.mariadb_batch_size)


def predictor_main(db, batch_size, mariadb_batch_size):
    main(db, batch_size, mariadb_batch_size)

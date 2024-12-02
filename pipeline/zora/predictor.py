import argparse
import gc
import os
import re

import nltk
import tensorflow as tf
from nltk import tokenize
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tensorflow import convert_to_tensor
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm
from transformers import BertTokenizer, TFBertMainLayer, TFBertModel

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

from settings.settings import PredictionSettings
predictor_settings = PredictionSettings()

#os.environ[PredictionSettings.CUDA_VISIBLE_DEVICES_KEY] = PredictionSettings.CUDA_VISIBLE_DEVICES_VALUE

# Setup Logging
from utils.logger import logger
logging = logger(predictor_settings.AURORA_PREDICTOR_LOG_NAME)

# Download nltk tokenizer if not already downloaded
nltk.download(predictor_settings.NLTK_TOKENIZER_PUNKT)
nltk.download(predictor_settings.NLTK_TOKENIZER_PUNKT_TAB)

# Initialize BERT tokenizer globally for reuse
tokenizer = BertTokenizer.from_pretrained(PredictionSettings.BERT_PRETRAINED_MODEL_NAME)

# Constants
MAX_LEN = PredictionSettings.MAX_SEQ_LENGTH

# Model Dir
model_dir = os.path.abspath(os.path.expanduser(PredictionSettings.MODEL_DIR))
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
print(os.listdir(model_dir))


# Tensorflow Verification
print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


def sort_model_files(model_files):
    """Sort model files based on the number in the filename."""
    return sorted(model_files, key=lambda x: int(re.findall(r"\d+", x)[0]))


# Add @tf.function to optimize repeated calls to predict
# @tf.function(reduce_retracing=True)
# https://www.tensorflow.org/guide/intro_to_graphs
def predict_batch(model, inputs, masks):
    """Make predictions for a batch using the TensorFlow model."""
    return model([inputs, masks], training=False)


def update_sdg_field(prediction_entry, model_file, prediction, precision=8):
    """Dynamically update the relevant SDG field for a prediction entry, rounding the value to a specified precision."""
    # Extract the SDG number from the model file name using regex
    sdg_number = re.search(r"\d+", model_file).group(0)

    # Construct the field name dynamically, e.g., 'sdg1', 'sdg2', etc.
    field_name = f"sdg{sdg_number}"

    # Convert TensorFlow EagerTensor to a NumPy value
    prediction_value = prediction.numpy()[
        0
    ]  # Convert TensorFlow tensor to NumPy array and get the first value

    # Format the prediction to the specified precision using string formatting
    rounded_prediction = float(f"{prediction_value:.{precision}f}")

    # Dynamically set the value of the appropriate field using setattr
    setattr(prediction_entry, field_name, rounded_prediction)

    logging.info(
        f"Updated {field_name} for publication {prediction_entry.publication_id} with value {rounded_prediction}, (original value was: {prediction_value})."
    )


def tokenize_abstracts(abstracts):
    """For given texts, adds '[CLS]' and '[SEP]' tokens
    at the beginning and the end of each sentence, respectively.
    """
    t_abstracts = []
    for abstract in abstracts:
        t_abstract = "[CLS] "
        for sentence in tokenize.sent_tokenize(abstract):
            t_abstract = t_abstract + sentence + " [SEP] "
        t_abstracts.append(t_abstract)
    return t_abstracts


def b_tokenize_abstracts(t_abstracts, max_len):
    """Tokenizes sentences with the help
    of a 'bert-base-multilingual-uncased' tokenizer.
    """
    b_t_abstracts = [tokenizer.tokenize(_)[:max_len] for _ in t_abstracts]
    return b_t_abstracts


def convert_to_ids(b_t_abstracts):
    """Converts tokens to its specific
    IDs in a bert vocabulary.
    """
    input_ids = [tokenizer.convert_tokens_to_ids(_) for _ in b_t_abstracts]
    return input_ids


def abstracts_to_ids(abstracts):
    """Tokenizes abstracts and converts
    tokens to their specific IDs
    in a bert vocabulary.
    """
    tokenized_abstracts = tokenize_abstracts(abstracts)
    b_tokenized_abstracts = b_tokenize_abstracts(tokenized_abstracts, MAX_LEN)
    ids = convert_to_ids(b_tokenized_abstracts)
    return ids


def pad_ids(input_ids, max_len):
    """Padds sequences of a given IDs."""
    p_input_ids = pad_sequences(
        input_ids, maxlen=max_len, dtype="long", truncating="post", padding="post"
    )
    return p_input_ids


def create_attention_masks(inputs):
    """Creates attention masks
    for a given seuquences.
    """
    masks = []
    for sequence in inputs:
        sequence_mask = [float(_ > 0) for _ in sequence]
        masks.append(sequence_mask)
    return masks

def load_model_from_path(model_path):
    """Load model and predict for a batch of publications."""
    logging.info(f"Loading model from {model_path}")
    model = load_model(
        model_path,
        custom_objects={"TFBertModel": TFBertModel, "TFBertMainLayer": TFBertMainLayer},
    )
    logging.info(f"Model {model_path} loaded.")

    return model

def predict(model, publications, batch_size):

    predictions = []

    for i in range(0, len(publications), batch_size):
        batch = publications[i: i + batch_size]

        # TODO: Add to settings for simpler config
        abstracts = [f"{pub.title}\n{pub.description}" for pub in batch]

        # Tokenization and preprocessing
        ids = abstracts_to_ids(abstracts)
        padded_ids = pad_ids(ids, MAX_LEN)
        masks = create_attention_masks(padded_ids)

        inputs = convert_to_tensor(padded_ids)
        masks = convert_to_tensor(masks)

        # Log tensor shapes before prediction
        logging.info(
            f"Batch {i // batch_size + 1}: Input shape: {inputs.shape}, Mask shape: {masks.shape}"
        )

        # Predict
        logging.info(
            f"Predicting batch {i // batch_size + 1} (Publications {batch[0].publication_id} to {batch[-1].publication_id})"
        )
        # batch_predictions = model.predict([inputs, masks])
        batch_predictions = predict_batch(model, inputs, masks)
        predictions.extend(batch_predictions)

    # Clear memory
    del model, abstracts, ids, padded_ids, masks, inputs, batch_predictions
    gc.collect()


    return predictions

def process_and_predict_in_stages(session, batch_size, mariadb_batch_size):
    """
    Perform staged prediction by loading one model at a time, predicting across all publications,
    and saving results in batches.
    """
    logging.info("Starting the staged prediction process...")

    # Fetch all publications that are not fully predicted
    publications = (
        session.query(Publication)
        #.join(SDGPrediction)
        #.filter(~SDGPrediction.prediction_model.in_(["Aurora"]))
        .all()
    )

    if not publications:
        logging.info("No publications to predict. Process complete.")
        return

    # List all model files from the directory
    model_files = [f for f in os.listdir(model_dir) if f.endswith(".h5")]

    if not model_files:
        logging.error(f"No model files found in {model_dir}.")
        return

    # Sort model files in ascending order by SDG number
    model_files = sort_model_files(model_files)

    # Process each publication for every model.
    # For each model, predict across all publications
    for model_idx, model_file in enumerate(model_files, start=1):
        model_path = os.path.join(model_dir, model_file)
        logging.info(
            f"Processing model: {model_file} (Model {model_idx} of {len(model_files)})"
        )

        # Flush progress bar
        print()

        # Add progress bars for prediction and uploading
        prediction_pbar = tqdm(total=len(publications), desc=f"Model {model_idx}: {model_file} - Predicting", unit="pub", position=0)
        upload_pbar = tqdm(total=len(publications), desc=f"Model {model_idx}: {model_file} - Uploading", unit="pub", position=1)

        try:
            # Load the model
            model = load_model_from_path(model_path)
        except Exception as e:
            logging.error(f"Error loading model {model_file}: {e}")
            continue  # Skip this model if there's an issue

        # Generate predictions for all publications
        predictions = []
        for i in range(0, len(publications), batch_size):
            batch = publications[i: i + batch_size]
            batch_predictions = predict(model, batch, batch_size)
            predictions.extend(batch_predictions)
            prediction_pbar.update(len(batch))  # Update progress bar for prediction

        # Close prediction progress bar
        prediction_pbar.close()

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
                prediction_entry = (
                    session.query(SDGPrediction)
                    .filter_by(publication_id=pub.publication_id)
                    .first()
                )
                print(prediction_entry)

                # Check if the prediction entry exists first before adding
                if not prediction_entry:
                    logging.info(
                        f"Prediction entry does not exists for publication {pub.publication_id}. Creating new record.")
                    # If the entry does not exist, create a new one
                    prediction_entry = SDGPrediction(
                        publication_id=pub.publication_id,
                        prediction_model="Aurora",
                    )
                    #session.add(prediction_entry) # THIS CAUSES DUPLICAITON
                else:
                    logging.info(
                        f"Prediction entry already exists for publication {pub.publication_id}. Updating existing record.")

                print(prediction_entry)

                # Dynamically update the relevant SDG field
                update_sdg_field(prediction_entry, model_file, prediction)

                # Update last predicted goal
                prediction_entry.last_predicted_goal = model_idx

                # Update model
                prediction_entry.prediction_model = "Aurora"

                # Add to the list of updated entries
                updated_entries.append(prediction_entry)

            # Perform bulk update
            if updated_entries:
                print(len(updated_entries), updated_entries)
                session.bulk_save_objects(updated_entries)
                try:
                    session.commit()
                    logging.info(
                        f"Batch {i // mariadb_batch_size + 1} predictions for model {model_file} saved."
                    )
                except Exception as e:
                    logging.error(f"Error committing batch {i // mariadb_batch_size + 1}: {e}")
                    session.rollback()  # Rollback on error

            # Update upload progress bar for each batch processed
            upload_pbar.update(len(batch))

        # Close upload progress bar
        upload_pbar.close()

        # Clear memory
        del predictions
        gc.collect()

    # Mark publications as fully predicted if all models were used
    try:
        session.query(SDGPrediction).filter(SDGPrediction.last_predicted_goal == len(model_files)).update(
            {"predicted": True}, synchronize_session=False
        )
        session.commit()
    except Exception as e:
        logging.error(f"Error marking publications as fully predicted: {e}")
        session.rollback()

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

    # Check if GPU is available
    if tf.config.list_physical_devices('GPU'):
        print("GPU is available")
    else:
        print("GPU is not available")

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

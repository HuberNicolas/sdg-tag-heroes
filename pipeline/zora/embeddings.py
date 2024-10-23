from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import sessionmaker
import tensorflow as tf
import torch

from models.base import Base
from models.author import Author
from models.division import Division
from models.faculty import Faculty
from models.institute import Institute
from models.sdg_prediction import SDGPrediction
from models.publication import Publication

from settings.settings import EmbeddingsSettings
embeddings_settings = EmbeddingsSettings()

# Setup Logging
from utils.logger import logger
logging = logger(embeddings_settings.EMBEDDINGS_LOG_NAME)

# Tensorflow Verification
print(tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(device)

class PublicationEmbeddingGenerator:
    def __init__(self, engine, batch_size=embeddings_settings.DEFAULT_BATCH_SIZE):
        self._encoder = SentenceTransformer(
            model_name_or_path=embeddings_settings.ENCODER_MODEL, device=embeddings_settings.ENCODER_DEVICE
        )
        self.batch_size = batch_size
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    @staticmethod
    def make_prompt(pub):
        """Generate a text prompt for embedding."""
        # Use the pattern from embeddings_settings
        return "\n".join([line.format(pub=pub) for line in embeddings_settings.ENCODER_CONTENT_PATTERN])

    def fetch_publications(self):
        """Fetch publications from the database."""
        session = self.Session()
        publications = session.query(Publication).all()
        logging.info(f"Fetched {len(publications)} publications...")
        session.close()
        return publications

    def encode_publications(self, publications):
        """Generate embeddings for a batch of publications."""
        prompts = [self.make_prompt(pub) for pub in publications]
        embeddings = self._encoder.encode(
            prompts, batch_size=self.batch_size, show_progress_bar=True
        )
        logging.info(f"Generated {len(embeddings)} encodings for {len(publications)} publications...")
        return embeddings

    def process_batch(self):
        """Fetch, encode, and return publications in batches."""
        publications = self.fetch_publications()
        logging.info(f"Fetched {len(publications)} publications from the database.")

        for i in range(0, len(publications), self.batch_size):
            batch = publications[i: i + self.batch_size]
            logging.info(f"Processing batch {i // self.batch_size + 1} with {len(batch)} publications.")

            embeddings = self.encode_publications(batch)
            logging.info(f"Completed processing batch {i // self.batch_size + 1}.")

            yield batch, embeddings

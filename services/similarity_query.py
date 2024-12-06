import argparse
from qdrant_client.http.models import Filter, SearchRequest, VectorParams, NamedVector
from sentence_transformers import SentenceTransformer
import logging

# Setup Logging
from utils.logger import logger
logging = logger("similarity_query_log")

# Load the encoder model
from settings.settings import EmbeddingsSettings
embeddings_settings = EmbeddingsSettings()

# Hardcoded user query (customize this as needed)
user_query = """
    I'm a car enthusiast who loves technology. 
    I'm curious about innovations in sustainable energy and green transportation. 
    I'm not very familiar with SDGs, but I'm interested in anything related to cars and environmental impact.
    """

class SimilarityQuery:
    def __init__(self, qdrant_client):
        self.qclient = qdrant_client
        self.encoder = SentenceTransformer(
            model_name_or_path=embeddings_settings.ENCODER_MODEL,
            device=embeddings_settings.ENCODER_DEVICE
        )
        logging.info(f"Initialized SimilarityQuery with encoder: {embeddings_settings.ENCODER_MODEL}")

    def generate_user_query_vector(self, user_query):
        """Generate embedding for the user query string."""
        try:
            query_vector = NamedVector(
                name=embeddings_settings.VECTOR_CONTENT_NAME,
                vector=self.encoder.encode(user_query).tolist()
            )
            logging.info("Successfully generated query vector.")
            return query_vector
        except Exception as e:
            logging.error(f"Failed to generate query vector: {e}")
            raise

    def search_publications(self, query_vector, collection_name, top_k=5):
        """Perform similarity search in Qdrant."""
        try:
            search_results = self.qclient.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=None,  # Add filters if needed
                limit=top_k
            )
            logging.info(f"Found {len(search_results)} matching publications.")
            return search_results
        except Exception as e:
            logging.error(f"Failed to search publications: {e}")
            raise

    def format_results(self, search_results):
        """Format the search results for display."""
        formatted_results = []
        for result in search_results:
            payload = result.payload
            formatted_results.append({
                "publication_id": payload.get("sql_id"),
                "title": payload.get("title"),
                "description": payload.get("description"),
                "score": result.score,
            })
        return formatted_results


def main(top_k, user_query):
    # Initialize Qdrant client
    from db.qdrantdb_connector import client as qdrant_client
    from settings.settings import LoaderSettings
    loader_settings = LoaderSettings()
    collection_name = loader_settings.PUBLICATIONS_COLLECTION_NAME

    # Initialize SimilarityQuery
    sq = SimilarityQuery(qdrant_client)

    # Generate user query vector
    logging.info("Encoding user query...")
    query_vector = sq.generate_user_query_vector(user_query)

    # Perform similarity search
    logging.info("Searching for similar publications...")
    search_results = sq.search_publications(query_vector, collection_name, top_k)

    # Format and return results
    logging.info("Formatting search results...")
    formatted_results = sq.format_results(search_results)

    logging.info(f"Top {top_k} results: {formatted_results}")
    return formatted_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a similarity search for publications in Qdrant.")
    parser.add_argument(
        "--top_k",
        type=int,
        default=5,
        help="Specify the number of top results to return (default: 5)."
    )

    args = parser.parse_args()
    results = main(args.top_k)

    print("Search Results:")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  ID: {result['publication_id']}")
        print(f"  Title: {result['title']}")
        print(f"  Description: {result['description']}")
        print(f"  Score: {result['score']}")

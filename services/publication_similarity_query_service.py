import time
from typing import List, Optional, Dict

from qdrant_client.http.models import Filter, FieldCondition, MatchAny
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from models.publications.publication import Publication
from schemas.services.publication_similarity_query_service import (
    FunctionResponsePublicationSimilaritySchema,
    PublicationSimilaritySchema,
)
from settings.settings import EmbeddingsSettings, QdrantDBSettings


class PublicationSimilarityQueryService:
    def __init__(self, qdrant_client, db: Session):
        self.qclient = qdrant_client
        self.db = db
        self.encoder = SentenceTransformer(
            model_name_or_path=EmbeddingsSettings().ENCODER_MODEL,
            device=EmbeddingsSettings().ENCODER_DEVICE
        )

    def generate_user_query_vector(self, user_query: str) -> List[float]:
        """Generate embedding for the user query string."""
        try:
            query_vector = self.encoder.encode(user_query).tolist()
            return query_vector
        except Exception as e:
            raise

    def search_publications(self, query_vector: List[float], collection_name: str, top_k: int = 5, publication_ids: Optional[List[int]] = None) -> List[Dict]:
        """Perform similarity search in Qdrant within a subset of publication IDs."""
        try:
            # Create a filter if publication IDs are provided
            query_filter = None
            if publication_ids:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="sql_id",
                            match=MatchAny(any=publication_ids)
                        )
                    ]
                )

            search_results = self.qclient.search(
                collection_name=collection_name,
                query_vector=(QdrantDBSettings().PUBLICATIONS_CONTENT_VECTOR_NAME, query_vector),  # Use named vector format
                query_filter=query_filter,  # Use the filter here
                limit=top_k
            )
            return search_results
        except Exception as e:
            raise

    def get_similar_publications(self, user_query: str, top_k: int, publication_ids: Optional[List[int]] = None) -> PublicationSimilaritySchema:
        """Main method to retrieve similar publications."""
        # Generate the query vector
        start = time.time()
        query_vector = self.generate_user_query_vector(user_query)
        query_building_time = time.time() - start

        # Perform the similarity search
        start = time.time()
        search_results = self.search_publications(
            query_vector=query_vector,
            collection_name=QdrantDBSettings().PUBLICATIONS_COLLECTION_NAME,
            top_k=top_k,
            publication_ids=publication_ids
        )
        search_time = time.time() - start

        # Extract publication IDs and similarity scores
        publication_scores = {result.payload[QdrantDBSettings.PUBLICATIONS_SQL_ID_PAYLOAD_FIELD_NAME]: result.score for result in search_results}
        publication_ids = list(publication_scores.keys())

        # Fetch publication details from the database
        publications = (
            self.db.query(Publication)
            .filter(Publication.publication_id.in_(publication_ids))
            .all()
        )

        # Build the results using FunctionResponsePublicationSimilaritySchema
        results = [
            FunctionResponsePublicationSimilaritySchema(
                publication_id=pub.publication_id,
                title=pub.title,
                abstract=pub.description,
                score=publication_scores.get(pub.publication_id, 0.0)
            )
            for pub in publications
        ]

        # Sort results by score in descending order
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)

        # Convert to API Response Schema
        return PublicationSimilaritySchema(
            query_building_time=query_building_time,
            search_time=search_time,
            user_query=user_query,
            results=[result.model_dump() for result in sorted_results]
        )

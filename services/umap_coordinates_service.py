import os
import time

import joblib
from sentence_transformers import SentenceTransformer

from schemas.dimensionality_reduction import UserCoordinatesSchema
from settings.settings import EmbeddingsSettings, ReducerSettings

embeddings_settings = EmbeddingsSettings()
reducer_settings = ReducerSettings()

class UMAPCoordinateService:
    def __init__(self):
        """
        Initialize the UMAPCoordinateService.
        """

        # Resolve the absolute path for the UMAP model directory
        base_dir = "/"

        self.umap_model_dir = os.path.abspath(os.path.join(base_dir, reducer_settings.UMAP_MODEL_PATH))

        self.embedding_model = SentenceTransformer(
            model_name_or_path=embeddings_settings.ENCODER_MODEL,
            device=embeddings_settings.ENCODER_DEVICE
        )

        if not os.path.exists(self.umap_model_dir):
            raise ValueError(f"UMAP model directory does not exist: {self.umap_model_dir}")

    def _embed_query(self, query: str):
        """
        Generate an embedding for the user query.

        :param query: User query as a string.
        :return: Embedding vector for the query.
        """
        return self.embedding_model.encode(query, show_progress_bar=False)

    def _load_umap_model(self, sdg: int, level: int):
        """
        Load the UMAP model for a specific SDG and level.

        :param sdg: SDG identifier (1-17).
        :param level: Level identifier (1-3).
        :return: UMAP model instance.
        """
        # TODO: do de-hardcode model confis
        model_path = os.path.join(self.umap_model_dir,f"config_15_0.0_2", f"SDG{sdg}.joblib")
        print(f"Loading UMAP model from {model_path}")
        if not os.path.exists(model_path):
            raise Exception(f"UMAP model for SDG{sdg}, Level{level} not found.")

        return joblib.load(model_path)

    def get_coordinates(self, query: str, sdg: int, level: int) -> UserCoordinatesSchema:
        """
        Calculate UMAP coordinates for a user query.

        :param query: User query as a string.
        :param sdg: SDG identifier (1-17).
        :param level: Level identifier (1-3).
        :return: UserCoordinatesSchema instance containing the x, y, z coordinates and timing data.
        """
        try:
            start = time.time()
            # Generate embedding for the query
            embedding = self._embed_query(query)
            end = time.time()
            embedding_time = end - start


            # Load the appropriate UMAP model
            start = time.time()
            umap_model = self._load_umap_model(sdg, level)
            end = time.time()
            model_loading_time = end - start

            # Transform the embedding using the UMAP model
            start = time.time()
            reduced_coordinates = umap_model.transform([embedding])[0]  # Transform returns a list of coordinates
            end = time.time()
            umap_reduction_transform_time = end - start

            # Return coordinates as a structured schema
            return UserCoordinatesSchema(
                x_coord=reduced_coordinates[0],
                y_coord=reduced_coordinates[1],
                z_coord=0.0,
                embedding_time=embedding_time,
                model_loading_time=model_loading_time,
                umap_reduction_transform_time=umap_reduction_transform_time
            )

        except Exception as e:
            raise e

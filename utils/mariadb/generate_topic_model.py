import numpy as np
import pandas as pd
import json
import time
import sys
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.representation import KeyBERTInspired, MaximalMarginalRelevance, TextGeneration, ZeroShotClassification
from transformers import pipeline
from sqlalchemy.orm import sessionmaker
from db.qdrantdb_connector import client as qdrantdb_client
from db.mariadb_connector import engine as mariadb_engine
from qdrant_client.http.models import Filter, MatchAny, FieldCondition
from models.publications.publication import Publication
from models.publications.dimensionality_reduction import DimensionalityReduction
from settings.sdg_descriptions import sdgs
from settings.settings import EmbeddingsSettings

embeddings_settings = EmbeddingsSettings()

# Establish MariaDB connection
Session = sessionmaker(bind=mariadb_engine)
db = Session()

LIMIT = 5000
# Step 1: Query Publications and Dimensionality Reduction Data
shorthand_filter = "UMAP-30-0.1-2"

# Fetch publications matching the shorthand
results = (
    db.query(Publication, DimensionalityReduction)
    .join(DimensionalityReduction, Publication.publication_id == DimensionalityReduction.publication_id)
    #.filter(DimensionalityReduction.reduction_shorthand == shorthand_filter)
    .limit(LIMIT)
    .all()
)

if not results:
    raise ValueError("No publications found with the specified shorthand.")

# Extract publication data and shorthand predictions
publications = [{"id": pub.publication_id, "description": pub.description, "title": pub.title} for pub, _ in results]
dim_reductions = {pub.publication_id: {"x": dr.x_coord, "y": dr.y_coord, "shorthand": dr.reduction_shorthand} for pub, dr in results}

# Step 2: Fetch Embeddings from Qdrant
publication_ids = [pub["id"] for pub in publications]

# Create filter condition for Qdrant
filter_condition = Filter(
    must=[
        FieldCondition(
            key="sql_id",
            match=MatchAny(any=publication_ids),
        )
    ]
)

# Query embeddings from Qdrant
result = qdrantdb_client.scroll(
    collection_name="publications-mt",
    scroll_filter=filter_condition,
    limit=100000000,  # Replace with appropriate limit
    with_payload=True,
    with_vectors=True,
)

publications_qdrant = result[0]

# Step 3: Merge SQL Data with Qdrant Embeddings
# Create a dictionary of embeddings for quick lookup
embeddings_dict = {pub.payload["sql_id"]: pub.vector["content"] for pub in publications_qdrant}

# Merge data
merged_data = []
for pub in publications:
    pub_id = pub["id"]
    if pub_id in embeddings_dict:
        merged_data.append({
            "id": pub_id,
            "description": pub["description"],
            "title": pub["title"],
            "x": dim_reductions[pub_id]["x"],
            "y": dim_reductions[pub_id]["y"],
            "shorthand": dim_reductions[pub_id]["shorthand"],
            "embedding": embeddings_dict[pub_id]
        })

if not merged_data:
    raise ValueError("No matching publications and embeddings found.")

class PubWrapper:
    def __init__(self, data):
        self.title = data.get("title")
        self.description = data.get("description")

# Step 4: Extract Separate Lists for Model Input
# Use ENCODER_CONTENT_PATTERN to create formatted content

content_pattern = embeddings_settings.ENCODER_CONTENT_PATTERN

docs = [
    "\n".join([pattern.format(pub=PubWrapper(item)) for pattern in content_pattern])  # Use the wrapper
    for item in merged_data
]  # Combined content for the model
print(f"Sample document: {docs[0]}")

ids = [item["id"] for item in merged_data]  # Publication IDs
print(f"Sample id: {ids[0]}")

embeddings = np.array([item["embedding"] for item in merged_data])  # Embeddings as NumPy array
print(f"Sample embedding: {embeddings[0]}")

dimreds = np.array([[item["x"], item["y"]] for item in merged_data]) # Extract (dimreds) as [[x, y], ...]
print(f"Sample dimreds: {dimreds[0]}")


print(f"Total documents: {len(docs)}, total embeddings: {len(embeddings)}, total ids: {len(ids)}, total embeddings: {len(dimreds)}")

# Topic Modeling Pipeline
class TopicModelPipeline:
    """
       A modular pipeline for creating a BERTopic model with advanced representation techniques.
    """
    def __init__(self, embedding_model="all-MiniLM-L6-v2"):
        """
               Initialize the pipeline with default settings.

               Args:
                   embedding_model (str): The name of the embedding model to use.
               """

        # Step 1: Embedding models
        # https://maartengr.github.io/BERTopic/getting_started/embeddings/embeddings.html
        self.embedding_model = embedding_model

    def create_topic_model(self, reduced_dimensions=None, **params):
        """
               Create a fully-configured BERTopic model.

               Args:
                   reduced_dimensions (np.ndarray | None): Precomputed reduced dimensions (e.g., x, y values).
                   dim_reduction_method (str): The dimensionality reduction method, either 'umap' or 'pca'.
                   dim_reduction_params (dict): Parameters for the dimensionality reduction model.
                   cluster_method (str): The name of the cluster method to use, either 'hdbscan', 'kmeans' or 'agglomerative'.
                   cluster_method_params (dict): Parameters for the cluster method.
                   vectorizer_method_params (dict): Parameters for the vectorizer method.
                   ctfidf_method_params (dict): Parameters for the ctfidf method.
                   representation_models_params (dict): Parameters for the representation models.
                   verbose (bool): Whether to enable verbose output.

               Returns:
                   BERTopic: Configured BERTopic model.
               """
        dim_reduction_params = params.get("dim_reduction_params", {})
        cluster_method_params = params.get("cluster_method_params", {})
        vectorizer_params = params.get("vectorizer_params", {})
        ctfidf_params = params.get("ctfidf_params", {})
        representation_params = params.get("representation_params", {})

        # Step 2: Dimensionality Reduction
        # https://maartengr.github.io/BERTopic/getting_started/dim_reduction/dim_reduction.html

        # Dimensionality Reduction
        if reduced_dimensions is not None:
            print("Using precomputed reduced dimensions.")
            dim_model = None  # Skip dimensionality reduction
        else:
            dim_reduction_params = params.get("dim_reduction_params", {})
            dim_model = self._get_dim_model(**dim_reduction_params)

        # Step 3: Clustering
        # https://maartengr.github.io/BERTopic/getting_started/clustering/clustering.html
        cluster_model = self._get_cluster_model(**cluster_method_params)

        # Step 4: Vectorizers
        # https://maartengr.github.io/BERTopic/getting_started/vectorizers/vectorizers.html
        """
                Private method to create the vectorizer model.

                Args:
                    **kwargs: Additional arguments for the vectorizer model.

                Returns:
                    object: Vectorizer model.
        """
        vectorizer_model = CountVectorizer(**vectorizer_params)

        # Step 5: c-TF-IDF
        """
                Private method to create the c-TF-IDF model.

                c-TF-IDF: Adjust TF-IDF representation cluster/categorical/topic level of a document level

                Args:
                    **kwargs: Additional arguments for the c-TF-IDF model.

                Returns:
                    object: c-TF-IDF model.
        """
        ctfidf_model = ClassTfidfTransformer(**ctfidf_params)

        # Step 6: Fine-Tune and Representation Models
        representation_models = self._get_representation_models(**representation_params)

        # Create BERTopic Model
        return BERTopic(
            embedding_model=self.embedding_model,
            umap_model=dim_model,  # None if reduced dimensions are provided
            hdbscan_model=cluster_model,
            vectorizer_model=vectorizer_model,
            representation_model=representation_models,
            ctfidf_model=ctfidf_model,
            verbose=params.get("verbose", True),
        )

    def _get_dim_model(self, method="umap", **kwargs):
        """
                Private method to create the dimensionality reduction model.

                Args:
                    method (str): The dimensionality reduction method, either 'umap' or 'pca'.
                    **kwargs: Additional arguments for the dimensionality reduction model.

                Returns:
                    object: Dimensionality reduction model.
                """
        return UMAP(**kwargs) if method.lower() == "umap" else PCA(**kwargs)

    def _get_cluster_model(self, method="hdbscan", **kwargs):
        """
                Private method to create the cluster model.

                Args:
                    method (str): The cluster method, either 'hdbscan', 'kmeans', or 'agglomerative'.
                    **kwargs: Additional arguments for the cluster model.

                Returns:
                    object: Cluster model.
                """
        if method.lower() == "hdbscan":
            return HDBSCAN(**kwargs)
        elif method.lower() == "kmeans":
            return KMeans(**kwargs)
        elif method.lower() == "agglomerative":
            return AgglomerativeClustering(**kwargs)
        raise ValueError(f"Unsupported cluster method: {method}")



    def _get_representation_models(self, **kwargs):
        """
               Create and configure advanced representation models for BERTopic.

               Args:
                    **kwargs: Additional arguments for the representation models, such as:
                   - diversity (float): The diversity parameter for MaximalMarginalRelevance.
                   - candidate_topics (list): A list of candidate topics for ZeroShotClassification.
                   - text_generator_model (str): Model name for text generation.

               Returns:
                   dict: Dictionary of representation models.
               """
        # Main representation model (KeyBERT-inspired)
        main_model = KeyBERTInspired()

        # Extract parameters or use defaults
        diversity = kwargs.get("diversity", 0.3)
        # Aspect-based models
        aspect_model_1 = MaximalMarginalRelevance(diversity=diversity)

        # Text-generation model
        generator = pipeline("text2text-generation", model="google/flan-t5-base")
        aspect_model_2 = TextGeneration(generator)

        # Zero-shot classification model
        candidate_topics = kwargs.get("candidate_topics", )
        candidate_topics = candidate_topics
        aspect_model_3 = ZeroShotClassification(candidate_topics, model="facebook/bart-large-mnli")

        # Combine into a representation model dictionary
        representation_models = {
            "Main": main_model,
            "Aspect1": aspect_model_1,
            "Aspect2": aspect_model_2,
            "Aspect3": aspect_model_3,
        }
        return representation_models

tm_pipeline = TopicModelPipeline()

# Combine seed words from all SDGs
N = 3  # Set the limit for seed words per SDG
seed_words = [word for sdg in sdgs for word in sdg.seed_words[:N]]
print(seed_words)

topic_model = tm_pipeline.create_topic_model(
    dim_reduction_params={"n_neighbors": 15 , "n_components": 2, "min_dist": 0.0, "metric": "cosine"},
    # reduced_dimensions=dimreds,
    cluster_method_params={"min_cluster_size": 15, "metric": "euclidean", "prediction_data": True},
    vectorizer_params={"stop_words": "english", "ngram_range": (1, 3), "min_df": 10, "max_features": 10_000},
    ctfidf_params={"bm25_weighting": True, "reduce_frequent_words": True},
    representation_params={"diversity": 0.5, "candidate_topics": seed_words},
)

start = time.time()
topic_model.fit(docs, embeddings)
print(f"Fitting took {time.time() - start:.2f}s")

# Data Export for Visualization
#topic_model.visualize_documents(docs, embeddings=embeddings)

# Step 1: Reduce Dimensionality to 2D
reduced_embeddings = topic_model._reduce_dimensionality(embeddings=embeddings)
print(f"Reduced embeddings shape: {reduced_embeddings.shape}")

# Ensure the embeddings are 2D
if reduced_embeddings.shape[1] != 2:
    reduced_embeddings = reduced_embeddings[:, :2]  # Use only the first two dimensions

# Step 2: Combine with Metadata
data = pd.DataFrame(reduced_embeddings, columns=["x", "y"])
data["id"] = ids  # Reuse the passed IDs
doc_info = topic_model.get_document_info(docs)
topic_info = topic_model.get_topic_info()
data["topic"] = doc_info["Topic"]
data["document"] = docs
data["keywords"] = doc_info["Representation"]

# Step 3: Export to JSON and CSV
data_json = data.to_dict(orient="records")
with open("topic_data.json", "w") as f:
    json.dump(data_json, f, indent=4)

data.to_csv("topic_data.csv", index=False)
topic_info.to_csv("topic_info.csv", index=False)

print("Data exported successfully!")


import os
from typing import ClassVar, List, Tuple

import pytz
from pydantic_settings import BaseSettings


class ProjectSettings(BaseSettings):
    APP_NAME: str = "iCoGaLa"
    DEBUG_MODE: bool = False

class SDGSettings(BaseSettings):
    SDGOAL_NUMBER: int = 17
    SDTARGET_NUMBER: int = 169


class EmbeddingsSettings(BaseSettings):
    EMBEDDINGS_LOG_NAME: ClassVar[str] = "embeddings.log"
    VECTOR_SIZE: ClassVar[int] = 384
    ENCODER_MODEL: ClassVar[str] = "sentence-transformers/all-MiniLM-L6-v2"
    ENCODER_DEVICE: ClassVar[str] = "cuda:0" # Either "cpu" or "cuda: 0"
    DEFAULT_BATCH_SIZE: ClassVar[int] = 32
    VECTOR_CONTENT_NAME: ClassVar[str] = "content"


    # Define the content pattern as a list of format strings
    ENCODER_CONTENT_PATTERN: ClassVar[List[str]] = [
        "Title: {pub.title}",
        # "Author: {', '.join([author.name for author in pub.authors])}",
        # "Date: {pub.date}",
        # "Publisher: {pub.publisher}",
        "Abstract: {pub.description}"
    ]

class LoaderSettings(BaseSettings):
    LOADER_LOG_NAME: ClassVar[str] = "loader.log"
    DEFAULT_BATCH_SIZE: ClassVar[int] = 64
    PUBLICATIONS_COLLECTION_NAME: ClassVar[str] = "publications-mt"


class TimeZoneSettings(BaseSettings):
    ZURICH_TZ_STRING: str = "Europe/Zurich" # Specify the timezone for Zurich
    ZURICH_TZ: ClassVar = pytz.timezone(ZURICH_TZ_STRING)

    # For Django
    DJANGO_TIME_ZONE: str = "CET" # Origin: "UTC"
    DJANGO_USE_TZ: bool = True



class LoggingSettings(BaseSettings):
    LOG_PATH: ClassVar[str] = "logs"
    LOG_FORMAT: ClassVar[str] = "%(asctime)s - %(levelname)s - %(message)s"

class PredictionSettings(BaseSettings):
    AURORA_PREDICTOR_LOG_NAME: ClassVar[str] = "predictor_aurora.log"
    DVDBLK_PREDICTOR_LOG_NAME: ClassVar[str] = "predictor_dvdblk.log"

    MODEL_DIR: ClassVar[str] = os.path.join("data", "pipeline", "aurora_models")
    AURORA_MODEL_GOAL_LINKS: ClassVar[str] = "aurora-model-goal-only-links.csv"

    CUDA_VISIBLE_DEVICES_KEY: ClassVar[str] = "CUDA_VISIBLE_DEVICES"
    CUDA_VISIBLE_DEVICES_VALUE: ClassVar[str] = "1"

    NLTK_TOKENIZER_PUNKT: ClassVar[str] = "punkt"
    NLTK_TOKENIZER_PUNKT_TAB: ClassVar[str] = "punkt_tab"

    BERT_PRETRAINED_MODEL_NAME: ClassVar[str] = "bert-base-multilingual-uncased"
    MAX_SEQ_LENGTH: ClassVar[int] = 512

    DEFAULT_BATCH_SIZE: ClassVar[int] = 16
    DEFAULT_MARIADB_BATCH_SIZE: ClassVar[int] = 500
    DEFAULT_DVDBLK_BATCH_SIZE: ClassVar[int] = 16


class TargetPredictionSettings(PredictionSettings):
    AURORA_TARGET_PREDICTOR_LOG_NAME: ClassVar[str] = "target_predictor_aurora.log"


class CollectorSettings(BaseSettings):
    COLLECTOR_LOG_NAME: ClassVar[str] = "collector.log"

    JSON_PATH: ClassVar[str] = "./data/pipeline/publications"
    NO_ABSTRACT_PUBLICATIONS_FOLDER_PATH: ClassVar[str] = "/missing_abstract"
    PUBLICATIONS_FOLDER_PATH: ClassVar[str] = "/full_publications"

    ZORA_BASE_URL: ClassVar[str] = "https://www.zora.uzh.ch/cgi/oai2"
    ZORA_SET_LIST_URL: ClassVar[str] = "https://www.zora.uzh.ch/cgi/oai2?verb=ListSets"

    PUBLICATION_LIMIT: ClassVar[int] = 300000

class ReducerSettings(BaseSettings):
    REDUCER_LOG_NAME: ClassVar[str] = "reducer.log"

    DEFAULT_MARIADB_BATCH_SIZE: ClassVar[int] = 500

    UMAP_N_NEIGHBORS: ClassVar[int] = 15
    UMAP_MIN_DIST: ClassVar[float] = 0.1
    UMAP_N_COMPONENTS: ClassVar[int] = 2

    # Arrays for UMAP parameter combinations
    UMAP_N_NEIGHBORS_ARRAY: ClassVar[List[int]] = [15, 30]
    UMAP_MIN_DIST_ARRAY: ClassVar[List[float]] = [0.1]
    UMAP_N_COMPONENTS_ARRAY: ClassVar[List[int]] = [2]  # Example array for n_components

    # Filter ranges
    FILTER_RANGES: ClassVar[List[Tuple[float, float]]] = [(1.0, 0.99), (0.99, 0.9), (0.9, 0.8)]  # SDG filter ranges



class PublicationsRouterSettings(BaseSettings):
    PUBLICATIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_publications.log"

class SDGsRouterSettings(BaseSettings):
    SDGS_ROUTER_LOG_NAME: ClassVar[str] = "api_sdgs.log"

class AuthorsRouterSettings(BaseSettings):
    AUTHORS_ROUTER_LOG_NAME: ClassVar[str] = "api_authors.log"

class SDGUserLabelsSettings(BaseSettings):
    SDGUSERLABELS_ROUTER_LOG_NAME: ClassVar[str] = "api_sdg_user_labels.log"

class VotesSettings(BaseSettings):
    VOTES_ROUTER_LOG_NAME: ClassVar[str] = "api_votes.log"

class AnnotationsSettings(BaseSettings):
    ANNOTATIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_annotations.log"

class DimensionalityReductionsRouterSettings(BaseSettings):
    DIMENSIONALITYREDUCTIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_dimensionality_reductions.log"

class AuthenticationRouterSettings(BaseSettings):
    AUTHENTICATION_ROUTER_LOG_NAME: ClassVar[str] = "api_authentication.log"
    CRYPT_CONTEXT_SCHEMA: ClassVar[str] = "bcrypt"
    CRYPT_CONTEXT_DEPRECATED: ClassVar[str] = "auto"
    TOKEN_URL: ClassVar[str] = "auth/token"

class MariaDBSettings(BaseSettings):
    MARIADB_CHARSET: ClassVar[str] = "utf8mb4"
    MARIADB_COLLATION: ClassVar[str] = "utf8mb4_unicode_ci"
    SQLALCHEMY_DEBUG_OUTPUT: ClassVar[bool] = False



class PrefectSettings(BaseSettings):
    PREFECT_LOG_NAME: ClassVar[str] = "prefect.log"

    DB_TYPE: ClassVar[str] = "mariadb"
    COLLECTOR_BATCH_SIZE: ClassVar[int] = 10
    COLLECTOR_RESET: ClassVar[str] = "true"
    PREDICTOR_BATCH_SIZE: ClassVar[int] = 64
    LOADER_BATCH_SIZE: ClassVar[int] = 64


class MongoDBSDGSettings(BaseSettings):
    DB_NAME: ClassVar[str] = "sdg_database"
    SVG_ENCODING: ClassVar[str] = "utf-8"
    GOAL_SVG_PATH_TEMPLATE: ClassVar[str] = "data/icons/Color_Goal_{goal_index}.svg"
    TARGET_SVG_PATH_TEMPLATE: ClassVar[str] = "data/icons/target/GOAL_{goal_index}_TARGET_{index}.svg"

class EnvLoaderSettings(BaseSettings):
    # Do not set this to True in prod as it will print secrets
    ENV_LOADER_DEBUG_OUTPUT: ClassVar[bool] = False

class BackendSettings(BaseSettings):
    BACKEND_LOG_NAME: ClassVar[str] = "backend.log"
    DJANGO_DEBUG_MODE: ClassVar[bool] = True
    LANGUAGE_CODE: str = "en-us"
    USE_I18N: ClassVar[bool] = True


class ExplainerSettings(BaseSettings):
    PROMPT_PATH: ClassVar[str] = "/prompts"

    # smaller model (cheapest as of 06.2024) to keep the cost down
    GPT_MODEL: ClassVar[str] = "gpt-3.5-turbo-0125"
    GPT_TEMPERATURE: ClassVar[float] = 0.2

import os
from typing import ClassVar, List, Tuple

import pytz
from pydantic_settings import BaseSettings


### Project Settings and Context

class ProjectSettings(BaseSettings):
    APP_NAME: str = "iCoGaLa"
    DEBUG_MODE: bool = False


class SDGSettings(BaseSettings):
    SDGOAL_NUMBER: int = 17
    SDTARGET_NUMBER: int = 169



### General Settings

class TimeZoneSettings(BaseSettings):
    ZURICH_TZ_STRING: str = "Europe/Zurich"  # Specify the timezone for Zurich
    ZURICH_TZ: ClassVar = pytz.timezone(ZURICH_TZ_STRING)


class LoggingSettings(BaseSettings):
    LOG_PATH: ClassVar[str] = "logs"
    LOG_FORMAT: ClassVar[str] = "{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"

class EnvLoaderSettings(BaseSettings):
    # Do not set this to True in prod as it will print secrets
    ENV_LOADER_DEBUG_OUTPUT: ClassVar[bool] = False

class FixturesSettings(BaseSettings):
    FIXTURES_LOG_NAME: ClassVar[str] = "fixtures.log"


### DB-Settings
class MariaDBSettings(BaseSettings):
    MARIADB_CHARSET: ClassVar[str] = "utf8mb4"
    MARIADB_COLLATION: ClassVar[str] = "utf8mb4_unicode_ci"
    SQLALCHEMY_DEBUG_OUTPUT: ClassVar[bool] = False
    MARIADB_LOG_NAME: ClassVar[str] = "db_mariadb.log"

class QdrantDBSettings(BaseSettings):
    QDRANTDB_LOG_NAME: ClassVar[str] = "db_qdrantdb.log"
    QDRANT_TIMEOUT: ClassVar[int] = 120
    PUBLICATIONS_COLLECTION_NAME: ClassVar[str] = "publications-mt" #TODO: remove duplicate and leave here; do NOT remove here
    PUBLICATIONS_CONTENT_VECTOR_NAME: ClassVar[str] = "content"
    PUBLICATIONS_SQL_ID_PAYLOAD_FIELD_NAME: ClassVar[str] = "sql_id"

class CouchDBSettings(BaseSettings):
    COUCHDB_LOG_NAME: ClassVar[str] = "db_couchdb.log"

class RedisDBSettings(BaseSettings):
    REDIS_LOG_NAME: ClassVar[str] = "db_redis.log"

class MongoDBSDGSettings(BaseSettings):
    MONGODB_LOG_NAME: ClassVar[str] = "db_mongodb.log"
    DB_NAME: ClassVar[str] = "sdg_database"
    DB_COLLECTION_NAME: ClassVar[str] = "explanations"
    SVG_ENCODING: ClassVar[str] = "utf-8"
    GOAL_SVG_PATH_TEMPLATE: ClassVar[str] = "data/icons/Color_Goal_{goal_index}.svg"
    TARGET_SVG_PATH_TEMPLATE: ClassVar[str] = (
        "data/icons/target/GOAL_{goal_index}_TARGET_{index}.svg"
    )



### Pipeline Settings
class EmbeddingsSettings(BaseSettings):
    EMBEDDINGS_LOG_NAME: ClassVar[str] = "embeddings.log"
    VECTOR_SIZE: ClassVar[int] = 384
    ENCODER_MODEL: ClassVar[str] = "sentence-transformers/all-MiniLM-L6-v2"
    ENCODER_DEVICE: ClassVar[str] = "cpu"  # Either "cpu" or "cuda: 0"
    DEFAULT_BATCH_SIZE: ClassVar[int] = 32
    VECTOR_CONTENT_NAME: ClassVar[str] = "content"

    # Define the content pattern as a list of format strings
    ENCODER_CONTENT_PATTERN: ClassVar[List[str]] = [
        "Title: {pub.title}",
        # "Author: {', '.join([author.name for author in pub.authors])}",
        # "Date: {pub.date}",
        # "Publisher: {pub.publisher}",
        "Abstract: {pub.description}",
    ]



# For Goals
class PredictionSettings(BaseSettings):
    AURORA_PREDICTOR_LOG_NAME: ClassVar[str] = "predictor_aurora.log"
    DVDBLK_PREDICTOR_LOG_NAME: ClassVar[str] = "predictor_dvdblk.log"

    MODEL_DIR: ClassVar[str] = os.path.join(
        "data", "pipeline", "aurora_models", "targets"
    )
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


# For Targets
class TargetPredictionSettings(PredictionSettings):
    AURORA_TARGET_PREDICTOR_LOG_NAME: ClassVar[str] = "target_predictor_aurora.log"

class LoaderSettings(BaseSettings):
    LOADER_LOG_NAME: ClassVar[str] = "loader.log"
    DEFAULT_BATCH_SIZE: ClassVar[int] = 64
    PUBLICATIONS_COLLECTION_NAME: ClassVar[str] = "publications-mt"

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

    # Model path
    UMAP_MODEL_PATH: ClassVar[str] = os.path.join("data", "api", "umap_model")

    # Filter ranges
    FILTER_RANGES: ClassVar[List[Tuple[float, float]]] = [
        (1.0, 0.9),
        (0.9, 0.8),
        (0.9, 0.5),
    ]  # SDG filter ranges

    MAP_PARTITION_SIZE: ClassVar[int] = 9

class PrefectSettings(BaseSettings):
    PREFECT_LOG_NAME: ClassVar[str] = "prefect.log"

    DB_TYPE: ClassVar[str] = "mariadb"
    COLLECTOR_BATCH_SIZE: ClassVar[int] = 10
    COLLECTOR_RESET: ClassVar[str] = "true"
    PREDICTOR_BATCH_SIZE: ClassVar[int] = 64
    LOADER_BATCH_SIZE: ClassVar[int] = 64




### Service Settings

class GPTAssistantServiceSettings(BaseSettings):
    PROMPT_PATH: ClassVar[str] = "/prompts"
    GPT_MODEL: ClassVar[str] = "gpt-4o-2024-08-06" # o4 required for Instructor library
    # smaller model (cheapest as of 06.2024) to keep the cost down: "gpt-3.5-turbo-0125"
    GPT_TEMPERATURE: ClassVar[float] = 0.2

class UserAnnotationAssessmentSettings(BaseSettings):
    GPT_MODEL: ClassVar[str] = "gpt-4o-2024-08-06"
    BERT_PRETRAINED_MODEL_NAME: ClassVar[str] = "distilbert-base-uncased"


class SimilaritySearchSettings(BaseSettings):
    SIMILARITY_SEARCH_LOG_NAME: ClassVar[str] = "similarity_search.log"


### Router Settings

class FastAPISettings(BaseSettings):
    FASTAPI_LOG_NAME: ClassVar[str] = "api_.log"


class AuthenticationRouterSettings(BaseSettings):
    AUTHENTICATION_ROUTER_LOG_NAME: ClassVar[str] = "api_authentication.log"
    CRYPT_CONTEXT_SCHEMA: ClassVar[str] = "bcrypt"
    CRYPT_CONTEXT_DEPRECATED: ClassVar[str] = "auto"
    TOKEN_URL: ClassVar[str] = "auth/token"

class UsersRouterSettings(BaseSettings):
    USERS_ROUTER_LOG_NAME: ClassVar[str] = "api_users.log"

class UserProfilesRouterSettings(BaseSettings):
    USER_PROFILES_ROUTER_LOG_NAME: ClassVar[str] = "api_user_profiles_.log"


class SDGsRouterSettings(BaseSettings):
    SDGS_ROUTER_LOG_NAME: ClassVar[str] = "api_sdgs.log"

class PublicationsRouterSettings(BaseSettings):
    PUBLICATIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_publications.log"

class AuthorsRouterSettings(BaseSettings):
    AUTHORS_ROUTER_LOG_NAME: ClassVar[str] = "api_authors.log"

class CollectionsRouterSettings(BaseSettings):
    COLLECTIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_collections.log"

class SDGPredictionsRouterSettings(BaseSettings):
    SDGPREDICTIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_sdg_predictions.log"
    DEFAULT_MODEL: ClassVar[str] = "Aurora" # "Dvdblk" and "Dvdblk_Softmax"

class DimensionalityReductionsRouterSettings(BaseSettings):
    DIMENSIONALITYREDUCTIONS_ROUTER_LOG_NAME: ClassVar[str] = (
        "api_dimensionality_reductions.log"
    )

class XPBanksRouterSettings(BaseSettings):
    XP_BANKS_ROUTER_LOG_NAME: ClassVar[str] = "api_xp_banks.log"

class CoinWalletsRouterSettings(BaseSettings):
    COIN_WALLETS_ROUTER_LOG_NAME: ClassVar[str] = "api_coin_wallets.log"

class ExplanationsRouterSettings(BaseSettings):
    EXPLANATIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_explanations.log"

class SDGSLabelSummariesRouterSettings(BaseSettings):
    SDGLABELSUMMARIES_ROUTER_LOG_NAME: ClassVar[str] = "api_sdg_label_summaries.log"


class SDGSLabelHistoriesRouterSettings(BaseSettings):
    SDGLABELHISTORIES_ROUTER_LOG_NAME: ClassVar[str] = "api_sdg_label_histories.log"

class SDGSLabelDecisionsRouterSettings(BaseSettings):
    SDGLABELDECISIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_sdg_label_decisions.log"

class SDGUserLabelsSettings(BaseSettings):
    SDGUSERLABELS_ROUTER_LOG_NAME: ClassVar[str] = "api_sdg_user_labels.log"


class AnnotationsSettings(BaseSettings):
    ANNOTATIONS_ROUTER_LOG_NAME: ClassVar[str] = "api_annotations.log"

class VotesSettings(BaseSettings):
    VOTES_ROUTER_LOG_NAME: ClassVar[str] = "api_votes.log"





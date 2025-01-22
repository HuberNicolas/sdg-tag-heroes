from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager

from api.app.routes import authentication
from api.app.routes import sdg_explanations
from api.app.routes import users
from api.app.routes import sdg_xp_banks
from api.app.routes import sdg_coin_wallets
from api.app.routes import publications
from api.app.routes import collections
from api.app.routes import sdgs
from api.app.routes import dimensionality_reductions
"""

from api.app.routes import authors
from api.app.routes import sdgs
from api.app.routes import votes
from api.app.routes import annotations
from api.app.routes import sdg_user_labels
from api.app.routes import dimensionality_reductions

from api.app.routes import sdg_predictions
from api.app.routes import profiles
#from api.app.routes import summaries # Way to slow w/o ChatGPT

from api.app.routes import sdg_coin_wallets
from api.app.routes import sdg_explanations
from api.app.routes import sdg_label_summaries
"""


from fastapi_pagination import add_pagination

from settings.settings import FastAPISettings
fastapi_settings = FastAPISettings()

# Setup Logging
from utils.logger import logger
logging = logger(fastapi_settings.FASTAPI_LOG_NAME)


# Import test utilities for each database
from db.mariadb_connector import test_mariadb_connection, conn as mariadb_conn
from db.mongodb_connector import test_mongodb_connection, client as mongo_client
from db.couchdb_connector import test_couchdb_connection, client as couchdb_client
from db.qdrantdb_connector import test_qdrant_connection, client as qdrant_client
from db.redisdb_connector import test_redis_connection, client as redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Initializing resources...")

    # Test MariaDB connection
    if test_mariadb_connection():
        logging.info("MariaDB connection is working.")
    else:
        logging.error("MariaDB connection failed!")

    # Test MongoDB connection
    if test_mongodb_connection():
        logging.info("MongoDB connection is working.")
    else:
        logging.error("MongoDB connection failed!")

    # Test CouchDB connection
    if test_couchdb_connection():
        logging.info("CouchDB connection is working.")
    else:
        logging.error("CouchDB connection failed!")

    # Test Qdrant connection
    if test_qdrant_connection():
        logging.info("Qdrant connection is working.")
    else:
        logging.error("Qdrant connection failed!")

    # Test Redis connection
    if test_redis_connection():
        logging.info("Redis connection is working.")
    else:
        logging.error("Redis connection failed!")

    yield  # Allow the application to run

    logging.info("Cleaning up resources...")

    # Cleanup logic
    try:
        mariadb_conn.close()
        logging.info("MariaDB connection closed.")
    except Exception as e:
        logging.warning(f"Error while closing MariaDB connection: {e}")

    try:
        mongo_client.close()
        logging.info("MongoDB client closed.")
    except Exception as e:
        logging.warning(f"Error while closing MongoDB client: {e}")

    try:
        couchdb_client.disconnect()
        logging.info("CouchDB client disconnected.")
    except Exception as e:
        logging.warning(f"Error while disconnecting CouchDB client: {e}")

    try:
        # Qdrant doesn't require explicit disconnection
        logging.info("Qdrant client cleanup completed.")
    except Exception as e:
        logging.warning(f"Error while cleaning up Qdrant client: {e}")

    try:
        redis_client.close()
        logging.info("Redis client closed.")
    except Exception as e:
        logging.warning(f"Error while closing Redis client: {e}")

app = FastAPI(lifespan=lifespan)
add_pagination(app)  # important! add pagination to your app
app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(sdg_xp_banks.router)
app.include_router(sdg_coin_wallets.router)
app.include_router(publications.router)
app.include_router(collections.router)
app.include_router(sdg_explanations.router)
app.include_router(sdgs.router)
app.include_router(dimensionality_reductions.router)
"""

app.include_router(authors.router)

app.include_router(votes.router)
app.include_router(annotations.router)
app.include_router(sdg_user_labels.router)
app.include_router(sdg_predictions.router)
app.include_router(profiles.router)
#app.include_router(summaries.router)


app.include_router(sdg_label_summaries.router)
"""


# CORS (development only)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Custom OpenAPI schema to include JWT in Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SDG Tag Heroes",
        version="1.0.0",
        description="API Documentation with JWT Authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply globally to all routes
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

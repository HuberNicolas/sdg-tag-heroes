from pymongo import MongoClient
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

from settings.settings import MongoDBSDGSettings
mongodb_settings = MongoDBSDGSettings()

# Setup Logging
from utils.logger import logger
logging = logger(mongodb_settings.MONGODB_LOG_NAME)

# Load the MongoDB environment variables
load_env('mongodb.env')

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch MongoDB connection details from environment variables
user = get_env_variable('MONGO_INITDB_ROOT_USERNAME')
password = get_env_variable('MONGO_INITDB_ROOT_PASSWORD')
host = get_env_variable('MONGODB_HOST') if running_in_docker else get_env_variable('MONGODB_HOST_LOCAL_IP')
port = get_env_variable('MONGODB_PORT') if running_in_docker else get_env_variable('MONGODB_PORT_LOCAL')
mongo_url = f"mongodb://{user}:{password}@{host}:{port}/"

# Log the connection details
logging.info(f"Connecting to MongoDB at {host}:{port} with user {user}")

# Establish connection to MongoDB
try:
    client = MongoClient(mongo_url)
    # List the databases
    databases = client.list_database_names()
    logging.info(f"Connection to MongoDB successful! Databases: {databases}")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")

def get_explanations_db():
    """
    Provides a connection to the sdg_explanations database.
    """
    return client['sdg_explanations']

def test_mongodb_connection():
    """
    Test the MongoDB connection by listing database names.
    """
    global client  # Ensure you're using the already established client
    try:
        databases = client.list_database_names()
        return True
    except Exception as e:
        logging.error(f"MongoDB connection test failed: {e}")
        return False

import logging
from pymongo import MongoClient
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
logger.info(f"Connecting to MongoDB at {host}:{port} with user {user}")

# Establish connection to MongoDB
try:
    client = MongoClient(mongo_url)
    # List the databases
    databases = client.list_database_names()
    logger.info(f"Connection to MongoDB successful! Databases: {databases}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

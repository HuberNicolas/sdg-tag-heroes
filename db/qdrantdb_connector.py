import logging
from qdrant_client import QdrantClient
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the Qdrant environment variables (if needed)
load_env('qdrantdb.env')

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch Qdrant connection details
host = get_env_variable('QDRANT_HOST') if running_in_docker else get_env_variable('QDRANT_HOST_LOCAL')
port = int(get_env_variable('QDRANT_PORT')) if running_in_docker else int(get_env_variable('QDRANT_PORT_LOCAL'))

# Log the connection details
logger.info(f"Connecting to Qdrant at {host}:{port}")

# Establish connection to Qdrant
try:
    client = QdrantClient(host=host, port=port, timeout=120)
    
    # Test the connection by listing collections
    collections = client.get_collections()
    logger.info(f"Connection to Qdrant successful! Collections: {collections.collections}")
    
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {e}")

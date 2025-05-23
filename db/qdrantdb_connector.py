from qdrant_client import QdrantClient
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

from settings.settings import QdrantDBSettings
qdrantdb_settings = QdrantDBSettings()

# Setup Logging
from utils.logger import logger
logging = logger(qdrantdb_settings.QDRANTDB_LOG_NAME)

# Load the Qdrant environment variables (if needed)
load_env('qdrantdb.env')

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch Qdrant connection details
host = get_env_variable('QDRANT_HOST') if running_in_docker else get_env_variable('QDRANT_HOST_LOCAL')
port = int(get_env_variable('QDRANT_PORT')) if running_in_docker else int(get_env_variable('QDRANT_PORT_LOCAL'))

# Log the connection details
logging.info(f"Connecting to Qdrant at {host}:{port}")

# Establish connection to Qdrant
try:
    client = QdrantClient(host=host, port=port, timeout=qdrantdb_settings.QDRANT_TIMEOUT)
    
    # Test the connection by listing collections
    collections = client.get_collections()
    logging.info(f"Connection to Qdrant successful! Collections: {collections.collections}")
    
except Exception as e:
    logging.error(f"Failed to connect to Qdrant: {e}")

def test_qdrant_connection():
    """
    Test the Qdrant connection by listing collections.
    """
    global client  # Ensure you're using the already established client
    try:
        collections = client.get_collections()
        logging.info(f"Qdrant connection test successful! Collections: {collections.collections}")
        return True
    except Exception as e:
        logging.error(f"Qdrant connection test failed: {e}")
        return False

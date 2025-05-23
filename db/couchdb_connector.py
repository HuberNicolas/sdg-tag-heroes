from cloudant.client import CouchDB
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

from settings.settings import CouchDBSettings
couchdb_settings = CouchDBSettings()

# Setup Logging
from utils.logger import logger
logging = logger(couchdb_settings.COUCHDB_LOG_NAME)

# Load the CouchDB environment variables
load_env('couchdb.env')

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch CouchDB connection details from environment variables
user = get_env_variable('COUCHDB_USER')
password = get_env_variable('COUCHDB_PASSWORD')

# Either container to container or local to container
host = get_env_variable('COUCHDB_HOST') if running_in_docker else get_env_variable('COUCHDB_HOST_LOCAL')
port = int(get_env_variable('COUCHDB_PORT')) if running_in_docker else int(get_env_variable('COUCHDB_PORT_LOCAL'))

couchdb_url = f"http://{host}:{port}"

# Log the connection details (avoid logging sensitive information like passwords in production)
logging.info(f"Connecting to CouchDB at {host}:{port} with user {user}")

# Establish connection to CouchDB
try:
    # Initialize the CouchDB server connection using cloudant
    client = CouchDB(user, password, url=couchdb_url, connect=True)
    
    # Check if the connection is established by listing databases
    databases = client.all_dbs()
    logging.info(f"Connection to CouchDB successful! Databases: {databases}")
    
    # Don't close connection here
    # client.disconnect()

except Exception as e:
    logging.error(f"Failed to connect to CouchDB: {e}")

def test_couchdb_connection():
    """
    Test the CouchDB connection by listing databases.
    """
    global client  # Ensure you're using the already established client
    try:
        databases = client.all_dbs()
        logging.info(f"CouchDB connection test successful! Databases: {databases}")
        return True
    except Exception as e:
        logging.error(f"CouchDB connection test failed: {e}")
        return False

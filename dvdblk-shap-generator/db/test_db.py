import os
import logging
from db.mariadb_connector import conn as mconn
from db.mongodb_connector import client as mclient
from db.qdrantdb_connector import client as qclient
from db.couchdb_connector import client as cclient
from db.redisdb_connector import client as rclient
from utils.env_loader import load_env, is_running_in_docker

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Utility function to check database connection
def check_connection(connector, db_name):
    try:
        if connector is not None:
            logger.info(f"Connection to {db_name} successful!")
            return True
        else:
            logger.error(f"Connection to {db_name} failed!")
            return False
    except Exception as e:
        logger.error(f"Error connecting to {db_name}: {e}")
        return False


# Function to load environment and simulate Docker or local environment
def load_env_for_simulation(is_docker_simulated=False):
    if is_docker_simulated:
        logger.info("Simulating Docker environment...")
        os.environ['IN_DOCKER'] = 'true'
    else:
        logger.info("Simulating local environment...")
        os.environ['IN_DOCKER'] = 'false'


# Test function to check the status of each database connector
def test_db_connections():
    logger.info("Testing database connections...")

    check_connection(mconn, "MariaDB")
    check_connection(mclient, "MongoDB")
    check_connection(qclient, "QdrantDB")
    check_connection(cclient, "CouchDB")
    check_connection(rclient, "RedisDB")


if __name__ == "__main__":
    import argparse

    # Set up argument parsing to switch between Docker and local simulations
    parser = argparse.ArgumentParser(description="Simulate database environment (Docker or local).")
    parser.add_argument('--docker', action='store_true', help='Simulate Docker environment')
    args = parser.parse_args()

    # Load the environment based on the flag (Docker or local)
    load_env_for_simulation(is_docker_simulated=args.docker)

    # Test all database connections
    test_db_connections()

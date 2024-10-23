import logging
import redis
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the Redis environment variables
load_env('redisdb.env')

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch Redis connection details from environment variables
user = get_env_variable('REDIS_USER')
password = get_env_variable('REDIS_PASSWORD')

# Either container to container or local to container
host = get_env_variable('REDIS_HOST') if running_in_docker else get_env_variable('REDIS_HOST_LOCAL')
port = get_env_variable('REDIS_PORT') if running_in_docker else get_env_variable('REDIS_PORT_LOCAL')

# Log the connection details
logger.info(f"Connecting to Redis at {host}:{port} with user {user}")

# Establish connection to Redis
try:
    # Create a Redis connection with authentication
    client = redis.StrictRedis(
        host=host,
        port=port,
        username=user,
        password=password,
        decode_responses=True
    )

    # Test connection by pinging Redis
    client.ping()
    logger.info(f"Connection to Redis successful!")

    # List keys in the current database (default is 0)
    logger.info("Listing all keys in the current database")
    keys = client.keys('*')  # List all keys
    logger.info(f"Keys in database 0: {keys}")
    print(f"Keys in database 0: {keys}")

except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")

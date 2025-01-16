from mysql.connector import connect
from sqlalchemy import create_engine
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

from settings.settings import MariaDBSettings

mariadb_settings = MariaDBSettings()

# Setup Logging
from utils.logger import logger
logging = logger(mariadb_settings.MARIADB_LOG_NAME)

# Load the mariadb environment variables
load_env('mariadb.env')

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch MariaDB connection details from environment variables
user = get_env_variable('MARIADB_USER')
password = get_env_variable('MARIADB_PASSWORD')
database_name = get_env_variable('MARIADB_DATABASE')

# Either container to container or local to container
host = get_env_variable('MARIADB_HOST') if running_in_docker else get_env_variable('MARIADB_HOST_LOCAL')
port = int(get_env_variable('MARIADB_PORT')) if running_in_docker else int(get_env_variable('MARIADB_PORT_LOCAL'))

# Log the connection details
logging.info(f"Connecting to MariaDB at {host}:{port} with user {user}")

# Establish connection to MariaDB with a compatible collation
try:
    conn = connect(
        host = host,
        port = port,
        user=user,
        password=password,
        charset=mariadb_settings.MARIADB_CHARSET,
        collation=mariadb_settings.MARIADB_COLLATION,
    )

    # Create a cursor and list the databases
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    logging.info(f"Connection to MariaDB successful! Databases: {[db[0] for db in databases]}")

    # Don't close connection here
    # conn.close()
except Exception as e:
    logging.error(f"Failed to connect to MariaDB: {e}")

# Create an SQLAlchemy engine for MariaDB without specifying a database
engine = None
try:
    sqlalchemy_host = host
    sqlalchemy_port = port

    engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{sqlalchemy_host}:{sqlalchemy_port}/{database_name}?charset={mariadb_settings.MARIADB_CHARSET}&collation={mariadb_settings.MARIADB_COLLATION}",
        echo=mariadb_settings.SQLALCHEMY_DEBUG_OUTPUT,  # Set to True to see SQLAlchemy generated SQL queries
        pool_size=10,           # Number of connections to keep in the pool
        max_overflow=20,        # Allow this many connections above pool_size
        pool_recycle=3600,      # Recycle connections after this many seconds
        pool_timeout=30         # Wait for this many seconds for a connection
    )
    logging.info("SQLAlchemy engine for MariaDB created successfully.")
except Exception as e:
    logging.error(f"Failed to create SQLAlchemy engine for MariaDB: {e}")


def test_mariadb_connection():
    """
    Test the MariaDB connection by executing a simple query.
    """
    global conn  # Ensure you're using the already established connection
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        return True
    except Exception as e:
        logging.error(f"MariaDB connection test failed: {e}")
        return False

import logging
from db.mariadb_connector import conn as mconn
from utils.env_loader import load_env, get_env_variable, is_running_in_docker

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the mariadb environment variables
load_env('mariadb.env')
database_name = get_env_variable('MARIADB_DATABASE')

def reset_all_tables(connection, database):
    try:
        # Create a cursor object
        cursor = connection.cursor()
        print(database)

        cursor.execute(f"USE `{database}`;")

        # Get the list of all tables in the current database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if not tables:
            logger.info("No tables found in the database.")
            return

        # Disable foreign key checks before dropping tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Drop each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
            logger.info(f"Dropped table: {table_name}")

        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        # Commit changes
        connection.commit()

        logger.info("All tables dropped successfully.")

    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    # Establish a connection using mysql.connector
    try:
        # Call the reset function
        reset_all_tables(mconn, database_name)
        
    except Exception as e:
        logger.error(f"Failed to connect to MariaDB: {e}")
    finally:
        mconn.close()

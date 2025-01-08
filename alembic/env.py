from logging.config import fileConfig
import logging
from alembic import context
from sqlalchemy import engine_from_config, pool, create_engine, text, inspect
from sqlalchemy.exc import OperationalError
from utils.env_loader import load_env, get_env_variable, is_running_in_docker
from settings.settings import MariaDBSettings  # Ensure this is correctly imported
from models.base import Base  # Replace with the actual import for your Base metadata

# Load environment variables
load_env("mariadb.env")

# MariaDB settings
mariadb_settings = MariaDBSettings()

# Determine if the script is running inside a Docker container
running_in_docker = is_running_in_docker()

# Fetch connection details
user = get_env_variable("MARIADB_USER")
password = get_env_variable("MARIADB_PASSWORD")
database_name = get_env_variable("MARIADB_DATABASE")
host = get_env_variable("MARIADB_HOST") if running_in_docker else get_env_variable("MARIADB_HOST_LOCAL")
port = str(get_env_variable("MARIADB_PORT")) if running_in_docker else str(get_env_variable("MARIADB_PORT_LOCAL"))
charset = mariadb_settings.MARIADB_CHARSET
collation = mariadb_settings.MARIADB_COLLATION

# Construct the SQLAlchemy URL with charset and collation
db_url = (
    f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database_name}"
    f"?charset={charset}&collation={collation}"
)

# Alembic configuration object
config = context.config
config.set_main_option("sqlalchemy.url", db_url)

# Metadata for autogeneration
target_metadata = Base.metadata

print("Tables registered in Base.metadata:")
print(Base.metadata.tables.keys())


# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic")  # Use the logger configured via fileConfig

def test_db_connection():
    """Test the database connection before running migrations."""
    try:
        engine = create_engine(db_url)

        # Inspect the database schema
        inspector = inspect(engine)
        db_tables = set(inspector.get_table_names())
        metadata_tables = set(Base.metadata.tables.keys())
        # Compare tables
        print("Tables in the database but not in metadata:", db_tables - metadata_tables)
        print("Tables in metadata but not in the database:", metadata_tables - db_tables)


        with engine.connect() as connection:
            connection.execute(text("SHOW databases"))  # Use sqlalchemy.text to create an executable object
        logging.info("Database connection successful!")
    except OperationalError as e:
        logging.error("Database connection failed!")
        logging.error(str(e))
        raise


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    logging.info("Running migrations in offline mode.")
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logging.info("Running migrations in online mode.")
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Test the connection before migrations
test_db_connection()

# Run the appropriate migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

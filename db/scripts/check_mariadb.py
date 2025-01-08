from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker

from models.base import Base

from db.mariadb_connector import engine as mariadb_engine  # MariaDB engine

# Initialize SQLAlchemy engine and session
engine = mariadb_engine
Session = sessionmaker(bind=engine)

# Function to log table creation
def log_table_creation(target, connection, **kwargs):
    print(f"Table '{target.name}' has been created.")

# Attach the 'after_create' event to all tables dynamically
for table_name, table_class in Base.registry._class_registry.items():
    if hasattr(table_class, '__table__'):
        event.listen(table_class.__table__, 'after_create', log_table_creation)

# Ensure tables are created
Base.metadata.create_all(engine)

# Print success message and table details
def print_table_summary(engine, session):
    print("\nSuccess! Database tables are set up.")
    print("\nList of tables and their row counts:")
    table_counter = 0

    inspector = inspect(engine)
    with session() as db_session:
        for table_name in inspector.get_table_names():
            table_counter += 1
            # Use the ORM to reflect tables dynamically
            table = Base.metadata.tables.get(table_name)
            if table is not None:
                row_count = db_session.query(table).count()
                print(f"Table '{table_name}': {row_count} rows")
            else:
                print(f"Table '{table_name}' is empty")

    print(f"\nTotal of {table_counter} tables.")

# Use a new session for fetching row counts
print_table_summary(engine, Session)

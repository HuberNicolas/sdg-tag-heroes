from sqlalchemy import event, inspect
from sqlalchemy.orm import sessionmaker


# Establish MariaDB connection
from db.mariadb_connector import engine as mariadb_engine
from models import Base


# Function to log table creation
def log_table_creation(target, connection, **kwargs):
    print(f"Table '{target.name}' has been created.")



def main() -> None:
    """
       Main function to set up the database schema and initiate a database session.
    """
    # Attach the 'after_create' event to all tables dynamically
    for table_name, table_class in Base.registry._class_registry.items():
        if hasattr(table_class, '__table__'):
            event.listen(table_class.__table__, 'after_create', log_table_creation)



    # Create a configured "Session" class bound to the MariaDB engine.
    Session = sessionmaker(bind=mariadb_engine)

    # Create all tables in the database based on the ORM models defined in Base.
    # This is equivalent to running SQL 'CREATE TABLE' statements for each model.
    Base.metadata.create_all(mariadb_engine)

    print("\nSuccess! Database tables are set up.")
    print("\nList of tables and their row counts:")
    table_counter = 0

    inspector = inspect(mariadb_engine)

    # Initiate a new session using the Session class.
    # The 'with' statement ensures the session is properly closed after use.
    with Session() as session:
        for table_name in inspector.get_table_names():
            table_counter += 1
            # Use the ORM to reflect tables dynamically
            table = Base.metadata.tables.get(table_name)
            if table is not None:
                row_count = session.query(table).count()
                print(f"Table '{table_name}': {row_count} rows")
            else:
                print(f"Table '{table_name}' is empty")

        print(f"\nTotal of {table_counter} tables.")


if __name__ == "__main__":
    main()

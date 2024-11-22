import re
from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models.sdg.clusters.publication_cluster import PublicationCluster  # Adjust import based on your project structure


def load_publication_clusters(file_path, batch_size=100):
    # Read the file containing only values
    with open(file_path, 'r') as f:
        file_content = f.read()

    # Extract individual tuples using regex
    tuples = re.findall(r"\(([^)]+)\)", file_content)

    data = []
    Session = sessionmaker(bind=mariadb_engine)

    for index, tuple_str in enumerate(tuples):
        # Skip empty or invalid lines
        if not tuple_str.strip():
            continue

        try:
            # Extract the individual fields, removing any surrounding quotes
            fields = [field.strip().strip("'") for field in tuple_str.split(',')]

            # Map fields to variables
            publication_id = int(fields[0])
            cluster_id = fields[1]
            sdg = int(fields[2]) if fields[2] != "NULL" else None
            level = int(fields[3]) if fields[3] != "NULL" else None
            topic = int(fields[4]) if fields[4] != "NULL" else None

            print(f"Adding record: publication_id={publication_id}, cluster_id={cluster_id}, sdg={sdg}, level={level}, topic={topic}")


            # Create a PublicationCluster object
            publication_cluster = PublicationCluster(
                publication_id=publication_id,
                cluster_id=cluster_id,
                cluster_id_string=cluster_id,
                sdg=sdg,
                level=level,
                topic=topic
            )
            data.append(publication_cluster)

            # Commit the batch once batch_size is reached
            if len(data) == batch_size:
                with Session() as session:
                    session.add_all(data)
                    session.commit()
                    print(f"Committed batch of {batch_size} records.")
                data.clear()  # Clear the list for the next batch

        except (IndexError, ValueError, TypeError) as e:
            print(f"Skipping invalid line: {tuple_str} - Error: {e}")
            continue

    # Commit any remaining data
    if data:
        with Session() as session:
            session.add_all(data)
            session.commit()
            print(f"Committed final batch of {len(data)} records.")


# Call the function with your file path
file_path = "./data/db/publications_clusters.txt"
load_publication_clusters(file_path, 500)

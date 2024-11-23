import re
from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models.sdg.clusters.publication_cluster import PublicationCluster  # Adjust import based on your project structure
from models.sdg.clusters.topic import ClusterTopic


def load_publication_clusters(file_path, batch_size=100):
    # Read the file containing only values
    with open(file_path, 'r') as f:
        file_content = f.read()

    # Extract individual tuples using regex
    tuples = re.findall(r"\(([^)]+)\)", file_content)

    data = []
    Session = sessionmaker(bind=mariadb_engine)

    for index, tuple_str in enumerate(tuples):
        if not tuple_str.strip():
            continue

        try:
            fields = [field.strip().strip("'") for field in tuple_str.split(',')]

            publication_id = int(fields[0])
            cluster_id_raw = fields[1]  # e.g., 'sdg10_level10_topic3'
            sdg = int(fields[2]) if fields[2] != "NULL" else None
            level = int(fields[3]) if fields[3] != "NULL" else None
            topic = int(fields[4]) if fields[4] != "NULL" else None

            # Add leading zeros to match the format in the database
            cluster_id = f"sdg{sdg:02}_level{level:02}_topic{topic:02}"

            # Resolve the topic_id from the ClusterTopic table
            with Session() as session:
                cluster_topic = session.query(ClusterTopic).filter_by(cluster_id_str=cluster_id).first()
                if not cluster_topic:
                    print(f"Cluster topic {cluster_id} not found, skipping.")
                    continue

                print(
                    f"Adding record: publication_id={publication_id}, cluster_id={cluster_topic.topic_id}, sdg={sdg}, level={level}, topic={topic}")

                publication_cluster = PublicationCluster(
                    publication_id=publication_id,
                    cluster_id=cluster_topic.topic_id,  # Use integer topic_id
                    cluster_id_string=cluster_id,  # Still store the string for reference
                    sdg=sdg,
                    level=level,
                    topic=topic
                )
                data.append(publication_cluster)

            if len(data) == batch_size:
                with Session() as session:
                    session.add_all(data)
                    session.commit()
                    print(f"Committed batch of {batch_size} records.")
                data.clear()

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

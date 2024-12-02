import json
import re
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models.sdg.clusters.topic import ClusterTopic
from models.sdg.clusters.group import ClusterGroup
from models.sdg.clusters.level import ClusterLevel
from settings.settings import TimeZoneSettings

# Initialize session
Session = sessionmaker(bind=mariadb_engine)
session = Session()

# Function to load data from JSON file
def load_data_from_json(file_path):

    with open(file_path, 'r') as file:
        data = json.load(file)

    current_timestamp = datetime.now(TimeZoneSettings.ZURICH_TZ)

    # Sort the SDG keys before processing
    sorted_sdgs = sorted(data.keys(), key=lambda sdg: int(re.search(r'\d+', sdg).group()))

    for sdg in sorted_sdgs:
        print(sdg)
        # Create ClusterGroup
        pattern = r'\d+'
        sdg_number = f"{int(re.search(pattern, sdg).group()):02}"
        group_name = f"cluster_group_sdg_{sdg_number}"
        cluster_group = ClusterGroup(
            name=group_name,
            created_at=current_timestamp,
            updated_at=current_timestamp
        )
        session.add(cluster_group)
        session.flush()  # To get the generated id

        levels = range(1, 26)
        for level in levels:
            # Create ClusterLevel
            cluster_level = ClusterLevel(
                cluster_group_id=cluster_group.id,
                level_number=level,
                created_at=current_timestamp,
                updated_at=current_timestamp
            )
            session.add(cluster_level)
            session.flush()  # To get the generated id

            level_str = str(level)
            if level_str in data[sdg]:
                centers = data[sdg][level_str].get('centers', [])
                sizes = data[sdg][level_str].get('sizes', [])
                labels = data[sdg][level_str].get('labels', [])

                for topic_index in range(0, level):
                    # Create ClusterTopic
                    cluster_topic = ClusterTopic(
                        level_id=cluster_level.id,
                        cluster_id_str=f"sdg{sdg_number}_level{int(level):02}_topic{int(topic_index + 1):02}",
                        size=sizes[topic_index],
                        center_x=centers[topic_index][0],
                        center_y=centers[topic_index][1],
                        name=f"topic{int(topic_index+1):02}",
                        topic_name=labels[topic_index],
                        created_at=current_timestamp,
                        updated_at=current_timestamp
                    )
                    session.add(cluster_topic)

    # Commit the session to save data
    session.commit()

load_data_from_json('./data/db/full_dataset_clusters.json')

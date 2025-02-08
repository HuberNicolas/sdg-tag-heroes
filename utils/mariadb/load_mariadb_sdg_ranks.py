import json
import re
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models import SDGRank
from settings.settings import TimeZoneSettings

# Initialize session
Session = sessionmaker(bind=mariadb_engine)
session = Session()

# Function to load data from JSON file
def load_sdgs_ranks_from_json(file_path):
    """
    Loads the ranks for each SDG goal (1-17) from a JSON file into the SDGRank table.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    current_timestamp = datetime.now(TimeZoneSettings.ZURICH_TZ)

    # SDG ranks are expected to be in tiers (0-3) for each SDG goal
    for sdg_id in range(1, 18):  # SDG 1 through 17
        for tier in range(4):  # Tiers 0 through 3
            # Get rank data from the JSON for the current SDG and tier
            rank_data = data.get(f"sdg_{sdg_id}", {}).get(f"tier_{tier}", {})

            # Get rank details (name, description, and XP required) or use defaults
            rank_name = rank_data.get("name")
            rank_description = rank_data.get("description")
            xp_required = rank_data.get("xp_required")

            # Create SDGRank entry for each SDG goal and its respective rank tier
            sdg_rank = SDGRank(
                sdg_goal_id=sdg_id,  # SDG Goal (1 to 17)
                tier=tier,  # Rank tier (0 to 3)
                name=rank_name,  # Name of the rank
                description=rank_description,  # Description of the rank
                xp_required=xp_required,  # XP required for this rank
            )
            session.add(sdg_rank)

    # Commit the session to save data
    session.commit()


# Call the function to load data from JSON file into the SDGRank table
load_sdgs_ranks_from_json('./data/ranks/sdg_ranks.json')

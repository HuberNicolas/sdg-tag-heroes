import json
from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models.sdgs.goal import SDGGoal

# Initialize session
Session = sessionmaker(bind=mariadb_engine)


def update_sdg_goals_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sdgs = json.load(f)

    with Session() as session:
        for sdg in sdgs:
            # Query existing SDGGoal record by id
            existing_goal = session.query(SDGGoal).filter(SDGGoal.id == sdg.get('id')).first()

            if existing_goal:
                # Update existing record with new values
                existing_goal.short_title = sdg.get('shortTitle')
                existing_goal.keywords = ', '.join(sdg.get('keywords', []))
                existing_goal.explanation = sdg.get('explanation')
            else:
                print(f"No existing SDGGoal found for id {sdg.get('id')}. Skipping update.")

        session.commit()
        print(f"Successfully updated SDG goals from {file_path}")


if __name__ == "__main__":
    file_path = "./data/icons/sdg_extras.json"
    update_sdg_goals_from_json(file_path)

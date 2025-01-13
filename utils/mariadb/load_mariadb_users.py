import os
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Inventory
from utils.env_loader import load_env
from models.users.user import User, UserRole
from models.users.labeler import Labeler
from models.users.expert import Expert
from models.users.admin import Admin

# Load environment variables
load_env("users.env")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_env_variable(key: str) -> str:
    """Retrieve environment variable or raise an error if missing."""
    value = os.getenv(key)
    if value is None:
        raise KeyError(f"Environment variable {key} is missing.")
    return value


def create_initial_users(session: Session):
    """Create initial users from environment variables."""
    user_count = int(get_env_variable("USER_COUNT"))

    for i in range(user_count):
        try:
            # Load user data from environment variables
            user_email = get_env_variable(f"USER_{i}_EMAIL")
            user_password = get_env_variable(f"USER_{i}_PASSWORD")
            user_roles_raw = get_env_variable(f"USER_{i}_ROLE")

            # Parse roles (split by comma and map to UserRole Enum)
            user_roles = []
            for role in user_roles_raw.split(","):
                role = role.strip()
                try:
                    user_roles.append(UserRole(role))
                except ValueError:
                    logger.warning(f"Unknown role {role} for user {user_email}")

            if not user_roles:
                logger.warning(f"No valid roles found for user {user_email}")
                continue

            # Check if the user already exists
            existing_user = session.query(User).filter(User.email == user_email).first()
            if existing_user:
                logger.info(f"User {user_email} already exists.")
                continue

            logger.info(f"Creating user {user_email} with roles {user_roles}")

            # Create the user
            user = User(email=user_email, roles=user_roles)
            user.set_password(user_password)

            # Create an inventory for the user
            inventory = Inventory(user=user)

            # Add user to role-specific tables
            if UserRole.ADMIN in user_roles:
                admin = Admin(user=user)
                session.add(admin)
            if UserRole.LABELER in user_roles:
                labeling_score = float(get_env_variable(f"USER_{i}_LABELING_SCORE"))
                labeler = Labeler(user=user, labeler_score=labeling_score)
                session.add(labeler)
            if UserRole.EXPERT in user_roles:
                labeling_score = float(get_env_variable(f"USER_{i}_LABELING_SCORE"))
                expert_score = float(get_env_variable(f"USER_{i}_EXPERT_SCORE"))
                expert = Expert(user=user, expert_score=expert_score)
                session.add(expert)

            session.add(inventory)

            # Commit the user to the database
            session.commit()
            logger.info(f"User {user_email} created successfully with roles {user_roles}.")

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Error creating user {i}: {e}")
        except KeyError as e:
            logger.error(f"Missing required environment variable for user {i}: {e}")
        except ValueError as e:
            logger.error(f"Invalid data for user {i}: {e}")



if __name__ == "__main__":
    from db.mariadb_connector import engine as mariadb_engine
    from models.base import Base
    from sqlalchemy.orm import sessionmaker

    # Setup database session
    Session = sessionmaker(bind=mariadb_engine)

    # Ensure tables are created
    Base.metadata.create_all(mariadb_engine)
    with Session() as session:
        create_initial_users(session)

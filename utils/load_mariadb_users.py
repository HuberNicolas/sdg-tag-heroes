import os
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils.env_loader import load_env
from models.user import User, UserRole
from models.labeler import Labeler
from models.expert import Expert
from models.admin import Admin

# Load environment variables
load_env("users.env")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_env_variable(key: str):
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
            user_role = get_env_variable(f"USER_{i}_ROLE")

            # Check if the user already exists
            existing_user = session.query(User).filter(User.email == user_email).first()
            if existing_user:
                logger.info(f"User {user_email} already exists.")
                continue

            logger.info(f"Creating user {user_email} with role {user_role}")

            # Handle role-specific logic
            if user_role == "admin":
                admin = Admin(email=user_email, role=UserRole.ADMIN)
                admin.set_password(user_password)
                session.add(admin)
            elif user_role == "labeler":
                labeling_score = float(get_env_variable(f"USER_{i}_LABELING_SCORE"))
                labeler = Labeler(email=user_email, role=UserRole.LABELER, labeling_score=labeling_score)
                labeler.set_password(user_password)
                session.add(labeler)
            elif user_role == "expert":
                labeling_score = float(get_env_variable(f"USER_{i}_LABELING_SCORE"))
                expert_score = float(get_env_variable(f"USER_{i}_EXPERT_SCORE"))
                expert = Expert(
                    email=user_email,
                    role=UserRole.EXPERT,
                    labeling_score=labeling_score,
                    expert_score=expert_score,
                )
                expert.set_password(user_password)
                session.add(expert)
            else:
                logger.warning(f"Unknown role {user_role} for user {user_email}")
                continue

            # Commit the user to the database
            session.commit()
            logger.info(f"User {user_email} created successfully.")

        except IntegrityError as e:
            session.rollback()
            logger.error(f"Error creating user {i}: {e}")
        except KeyError as e:
            logger.error(f"Missing required environment variable for user {i}: {e}")
        except ValueError as e:
            logger.error(f"Invalid data for user {i}: {e}")


if __name__ == "__main__":
    from db.mariadb_connector import engine as mariadb_engine
    from sqlalchemy.orm import sessionmaker

    # Setup database session
    Session = sessionmaker(bind=mariadb_engine)
    with Session() as session:
        create_initial_users(session)

import logging
from random import choice, randint, uniform

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from faker import Faker

from models import (
    SDGUserLabel,
    Vote,
    Annotation,
    SDGLabelDecision,
    Expert,
    SDGLabelHistory,
    Publication,
    User,
)
from db.mariadb_connector import engine as mariadb_engine
from models.base import Base
from models.sdg_label_decision import DecisionType
from models.vote import VoteType

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Faker instance
faker = Faker()
# Set Seed
faker.seed_instance(31011997)

def truncate_tables(session: Session, tables: list):
    """
    Truncate specified tables in the database.
    """
    logger.info("Truncating tables...")
    session.execute(text(f"SET foreign_key_checks = 0;"))
    for table in tables:
        session.execute(text(f"TRUNCATE TABLE {table};"))
    session.execute(text(f"SET foreign_key_checks = 1;"))
    session.commit()
    logger.info("Tables truncated successfully.")


def load_users(session: Session, max_users: int = 10):
    """
    Load a subset of users from the database.
    """
    users = session.query(User).limit(max_users).all()
    if not users:
        logger.error("No users found in the database.")
    return users


def load_publications(session: Session, max_pubs: int = 10):
    """
    Load a subset of publications from the database.
    """
    publications = session.query(Publication).limit(max_pubs).all()
    if not publications:
        logger.error("No publications found in the database.")
    return publications


def load_experts(session: Session):
    """
    Load all experts from the database.
    """
    experts = session.query(Expert).all()
    if not experts:
        logger.error("No experts found in the database.")
    return experts


def create_sdg_user_labels(session: Session, users: list[User], num_labels: int = 10):
    """
    Create SDGUserLabels and store them in the database.
    """
    logger.info("Creating SDGUserLabels...")
    labels = []
    for _ in range(num_labels):
        label = SDGUserLabel(
            user_id=choice(users).user_id,
            proposed_label=randint(0, 17),
            voted_label=randint(0, 17),
            description=faker.sentence(),
            labeled_at=faker.date_time_this_year(),
            created_at=faker.date_time_this_year(),
            updated_at=faker.date_time_this_year(),
        )
        session.add(label)
        labels.append(label)
    session.commit()
    logger.info(f"Created {num_labels} SDGUserLabels.")
    return labels


def create_votes(session: Session, users: list[User], user_labels: list[SDGUserLabel], num_votes: int = 20):
    """
    Create Votes and store them in the database.
    """
    logger.info("Creating Votes...")
    votes = []
    for _ in range(num_votes):
        vote = Vote(
            user_id=choice(users).user_id,
            sdg_user_label_id=choice(user_labels).label_id,
            vote_type=choice(["positive", "neutral", "negative"]),
            score=round(uniform(0, 5), 2),
            created_at=faker.date_time_this_year(),
        )
        session.add(vote)
        votes.append(vote)
    session.commit()
    logger.info(f"Created {num_votes} Votes.")
    return votes


def create_annotations(session: Session, users: list[User], user_labels: list[SDGUserLabel], num_annotations: int = 15):
    """
    Create Annotations and store them in the database.
    """
    logger.info("Creating Annotations...")
    annotations = []
    for _ in range(num_annotations):
        annotation = Annotation(
            user_id=choice(users).user_id,
            sdg_user_label_id=choice(user_labels).label_id,
            labeler_score=round(uniform(1.0, 100.0), 2),
            comment=faker.paragraph(),
            created_at=faker.date_time_this_year(),
            updated_at=faker.date_time_this_year(),
        )
        session.add(annotation)
        annotations.append(annotation)
    session.commit()
    logger.info(f"Created {num_annotations} Annotations.")
    return annotations


def create_sdg_label_decisions(
    session: Session, histories: list[SDGLabelHistory], user_labels: list[SDGUserLabel], experts: list[Expert], num_decisions: int = 10
):
    """
    Create SDGLabelDecisions and store them in the database.
    """
    logger.info("Creating SDGLabelDecisions...")
    decisions = []
    for _ in range(num_decisions):
        history = choice(histories)
        expert = choice(experts)
        decision = SDGLabelDecision(
            history_id=history.history_id,
            expert_id=expert.expert_id,
            suggested_label=randint(1, 17),  # Random SDG goal between 1 and 17
            decided_label=randint(1, 17),  # Random SDG goal between 1 and 17
            decision_type=choice(list(DecisionType)),  # Random decision type
            comment=faker.text(max_nb_chars=200),
            decided_at=faker.date_time_this_year(),
            created_at=faker.date_time_this_year(),
            updated_at=faker.date_time_this_year(),
        )
        # Assign a random subset of unique user labels to the decision
        num_labels = randint(1, 3)
        unique_labels = faker.random_elements(user_labels, length=num_labels, unique=True)
        decision.user_labels.extend(unique_labels)

        session.add(decision)
        decisions.append(decision)
    session.commit()
    unfinished_decisions = []

    for _ in range(num_decisions):
        history = choice(histories)
        expert = choice(experts)
        decision = SDGLabelDecision(
            history_id=history.history_id,
            suggested_label=randint(1, 17),  # Random SDG goal between 1 and 17
            decided_label=-1,
            decision_type=choice(list(DecisionType)),  # Random decision type
            comment=choice(list(["Not decided yet", None])),
            created_at=faker.date_time_this_year(),
            updated_at=faker.date_time_this_year(),
        )
        # Assign a random subset of unique user labels to the decision
        num_labels = randint(1, 3)
        unique_labels = faker.random_elements(user_labels, length=num_labels, unique=True)
        decision.user_labels.extend(unique_labels)

        session.add(decision)
        unfinished_decisions.append(decision)
    session.commit()

    logger.info(f"Created {num_decisions} SDGLabelDecisions.")
    logger.info(f"Created {num_decisions} unfinished SDGLabelDecisions.")
    return decisions

def create_votes_for_annotations(session: Session, annotations: list[Annotation], users: list[User], num_votes: int = 20):
    """
    Create Votes attached to Annotations and store them in the database.
    """
    logger.info("Creating Votes for Annotations...")
    votes = []
    for _ in range(num_votes):
        annotation = choice(annotations)
        user = choice(users)

        # Ensure the user hasn't already voted on this annotation
        existing_vote = session.query(Vote).filter_by(annotation_id=annotation.annotation_id, user_id=user.user_id).first()
        if existing_vote:
            continue

        # Create a new vote
        vote = Vote(
            user_id=user.user_id,
            annotation_id=annotation.annotation_id,
            vote_type=choice(list(VoteType)),
            score=round(faker.random_number(digits=2) / 100, 2),  # Random score between 0.0 and 100.0
            created_at=faker.date_time_this_year(),
        )

        session.add(vote)
        votes.append(vote)
    session.commit()
    logger.info(f"Created {len(votes)} Votes for Annotations.")
    return votes

def populate_db(
    session: Session,
    truncate: bool = False,
    max_users: int = 2,
    max_pubs: int = 2,
    num_labels: int = 4,
    num_votes: int = 10,
    num_annotations: int = 5,
    num_decisions: int = 4,
):
    """
    Populate the database with fixtures for SDGUserLabel, Vote, Annotation, and SDGLabelDecision.
    Optionally truncates the relevant tables before insertion.
    """
    try:
        # Truncate tables if the flag is set
        if truncate:
            truncate_tables(session, ["sdg_user_labels", "votes", "annotations", "sdg_label_decisions", "sdg_label_decision_user_label"])

        # Load users, publications, and experts
        users = load_users(session, max_users)
        publications = load_publications(session, max_pubs)
        experts = load_experts(session)

        if not users or not publications or not experts:
            logger.error("Users, Publications, or Experts not found in the database. Exiting.")
            return

        # Fetch existing SDGLabelHistories
        histories = session.query(SDGLabelHistory).all()
        if not histories:
            logger.error("No SDGLabelHistories found in the database.")
            return

        # Create SDGUserLabels
        user_labels = create_sdg_user_labels(session, users, num_labels)

        # Create Votes
        create_votes(session, users, user_labels, num_votes)

        # Create Annotations
        create_annotations(session, users, user_labels, num_annotations)

        # Create Votes for Annotations
        annotations = create_annotations(session, users, user_labels, num_annotations)
        create_votes_for_annotations(session, annotations, users, num_votes)

        # Create SDGLabelDecisions
        create_sdg_label_decisions(session, histories, user_labels, experts, num_decisions)

        logger.info("Database population completed successfully.")

    except IntegrityError as e:
        session.rollback()
        logger.error(f"IntegrityError encountered: {e}")

    except Exception as e:
        session.rollback()
        logger.error(f"An error occurred during database population: {e}")


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=mariadb_engine)

    # Ensure tables are created
    Base.metadata.create_all(mariadb_engine)

    with Session() as session:
        populate_db(session, truncate=True)

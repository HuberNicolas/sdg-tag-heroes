import random
from datetime import datetime
from random import choice, randint, uniform
from typing import List

from sqlalchemy import text, func
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
    User, SDGCoinWallet, SDGXPBank, SDGCoinWalletHistory, SDGXPBankHistory, SDGLabelSummary,
)
from db.mariadb_connector import engine as mariadb_engine
from models.base import Base
from enums.enums import SDGType, DecisionType, VoteType, ScenarioType
from services.gpt.gpt_assistant_service import GPTAssistantService
from services.gpt.strategies.persona_comment_generator_strategy import GenerateCommentStrategy, GenerateAnnotationStrategy
from utils.logger import logger
from settings.settings import FixturesSettings
from utils.personas.personas_generator import assign_personas

fixtures_settings = FixturesSettings()

logging = logger(fixtures_settings.FIXTURES_LOG_NAME)


# Faker instance
faker = Faker()
# Set Seed
SEED = 31011997
faker.seed_instance(SEED)
random.seed(SEED)

# Initialize GPT Service
gpt_service = GPTAssistantService()

def truncate_tables(session: Session, tables: list):
    """
    Truncate specified tables in the database.
    """
    logging.info("Truncating tables...")
    session.execute(text(f"SET foreign_key_checks = 0;"))
    for table in tables:
        session.execute(text(f"TRUNCATE TABLE {table};"))
    session.execute(text(f"SET foreign_key_checks = 1;"))
    session.commit()
    logging.info("Tables truncated successfully.")


def load_users(session: Session, max_users: int = 11):
    """
    Load a subset of users from the database.
    """
    users = session.query(User).limit(max_users).all()
    if not users:
        logging.error("No users found in the database.")
    return users


def load_publications(session: Session, max_pubs: int = 10):
    """
    Load a subset of publications from the database.
    """
    publications = session.query(Publication).limit(max_pubs).all()
    if not publications:
        logging.error("No publications found in the database.")
    return publications

def load_relevant_publications_with_sdg_labels(session: Session, max_pubs: int = 500) -> List[Publication]:
    """
    Load a subset of publications that have at least one SDG label set to 1 in their SDGLabelSummary.
    """
    publications = (
        session.query(Publication)
        .join(SDGLabelSummary)
        .filter(
            (SDGLabelSummary.sdg1 == 1) |
            (SDGLabelSummary.sdg2 == 1) |
            (SDGLabelSummary.sdg3 == 1) |
            (SDGLabelSummary.sdg4 == 1) |
            (SDGLabelSummary.sdg5 == 1) |
            (SDGLabelSummary.sdg6 == 1) |
            (SDGLabelSummary.sdg7 == 1) |
            (SDGLabelSummary.sdg8 == 1) |
            (SDGLabelSummary.sdg9 == 1) |
            (SDGLabelSummary.sdg10 == 1) |
            (SDGLabelSummary.sdg11 == 1) |
            (SDGLabelSummary.sdg12 == 1) |
            (SDGLabelSummary.sdg13 == 1) |
            (SDGLabelSummary.sdg14 == 1) |
            (SDGLabelSummary.sdg15 == 1) |
            (SDGLabelSummary.sdg16 == 1) |
            (SDGLabelSummary.sdg17 == 1)
        )
        .limit(max_pubs)
        .all()
    )
    if not publications:
        logging.error("No relevant publications found in the database.")
    return publications

def load_experts(session: Session):
    """
    Load all experts from the database.
    """
    experts = session.query(Expert).all()
    if not experts:
        logging.error("No experts found in the database.")
    return experts


def create_sdg_user_labels(session: Session, users: list[User], publications: list[Publication], num_labels: int = 10):
    """
    Create SDGUserLabels and store them in the database.
    """
    logging.info("Creating SDGUserLabels...")
    labels = []
    for _ in range(num_labels):
        label = SDGUserLabel(
            user_id=choice(users).user_id,
            publication_id=choice(publications).publication_id,
            proposed_label=randint(0, 17),
            voted_label=randint(0, 17),
            abstract_section=faker.sentence(),
            comment=faker.sentence(),
            labeled_at=datetime.now(),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        session.add(label)
        logging.info(f"Created {label}.")
        labels.append(label)
    session.commit()
    logging.info(f"Created {num_labels} SDGUserLabels.")
    return labels


def create_votes(session: Session, users: list[User], user_labels: list[SDGUserLabel], num_votes: int = 20):
    """
    Create Votes and store them in the database.
    """
    logging.info("Creating Votes...")
    votes = []
    for _ in range(num_votes):
        vote = Vote(
            user_id=choice(users).user_id,
            sdg_user_label_id=choice(user_labels).label_id,
            vote_type=choice(list(VoteType)),
            score=round(uniform(0, 5), 2),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        session.add(vote)
        logging.info(f"Created {vote}.")
        votes.append(vote)
    session.commit()
    logging.info(f"Created {num_votes} Votes.")
    return votes


def create_annotations(session: Session, users: list[User], user_labels: list[SDGUserLabel], num_annotations: int = 15):
    """
    Create Annotations and store them in the database.
    """
    logging.info("Creating Annotations...")
    annotations = []
    for _ in range(num_annotations):
        annotation = Annotation(
            user_id=choice(users).user_id,
            sdg_user_label_id=choice(user_labels).label_id,
            labeler_score=round(uniform(1.0, 100.0), 2),
            comment=faker.paragraph(),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        session.add(annotation)
        logging.info(f"Created {annotation}.")
        annotations.append(annotation)
    session.commit()
    logging.info(f"Created {num_annotations} Annotations.")
    return annotations


def create_sdg_label_decisions(
    session: Session, histories: list[SDGLabelHistory], user_labels: list[SDGUserLabel], experts: list[Expert], publications: list[Publication], num_decisions: int = 10
):
    """
    Create SDGLabelDecisions and store them in the database.
    """
    logging.info("Creating SDGLabelDecisions...")

    decisions = []
    for _ in range(num_decisions):
        history = choice(histories)
        expert = choice(experts)
        decision = SDGLabelDecision(
            history_id=history.history_id,
            expert_id=expert.expert_id,
            publication_id=choice(publications).publication_id, # Ensure decision is linked to a publication
            suggested_label=randint(1, 18), # Random SDG goal between 1 and 17, 0 not decided, 18 zero class
            decided_label=randint(1, 18), # Random SDG goal between 1 and 17, 0 not decided, 18 zero class
            decision_type=DecisionType.CONSENSUS_MAJORITY, # choice(list(DecisionType)),  # Random decision type
            scenario_type=choice(list(ScenarioType)),
            comment=faker.text(max_nb_chars=200),
            decided_at=datetime.now(),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        # Assign a random subset of unique user labels to the decision
        num_labels = randint(1, 3)
        unique_labels = faker.random_elements(user_labels, length=num_labels, unique=True)
        decision.user_labels.extend(unique_labels)

        session.add(decision)
        logging.info(f"Created {decision}.")
        decisions.append(decision)
    session.commit()




    unfinished_decisions = []
    for _ in range(num_decisions):
        history = choice(histories)
        expert = choice(experts)
        decision = SDGLabelDecision(
            history_id=history.history_id,
            publication_id=choice(publications).publication_id,  # Ensure decision is linked to a publication
            suggested_label=randint(1, 17), # Random SDG goal between 1 and 17, 0 not decided, 18 zero class
            decided_label=0,  # Random SDG goal between 1 and 17, 0 not decided, 18 zero class
            decision_type=DecisionType.CONSENSUS_MAJORITY, # choice(list(DecisionType)),  # Random decision type
            scenario_type=choice(list(ScenarioType)),
            comment=choice(list(["Not decided yet", None])),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        # Assign a random subset of unique user labels to the decision
        num_labels = randint(1, 3)
        unique_labels = faker.random_elements(user_labels, length=num_labels, unique=True)
        decision.user_labels.extend(unique_labels)

        session.add(decision)
        logging.info(f"Created {decision}.")
        unfinished_decisions.append(decision)
    session.commit()

    logging.info(f"Created {num_decisions} SDGLabelDecisions.")
    logging.info(f"Created {num_decisions} unfinished SDGLabelDecisions.")
    return decisions

def create_wallets(session: Session, users: list[User]):
    """
    Create SDGCoinWallets for each user.
    """
    logging.info("Creating SDGCoinWallets...")
    wallets = []
    for user in users:
        wallet = SDGCoinWallet(
            user_id=user.user_id,
            total_coins=round(uniform(0, 1000), 2),  # Random initial coin balance
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        session.add(wallet)
        logging.info(f"Created {wallet}.")
        wallets.append(wallet)
    session.commit()
    logging.info(f"Created {len(wallets)} SDGCoinWallets.")
    return wallets

def create_wallet_histories(session: Session, wallets: list[SDGCoinWallet], num_entries: int = 5):
    """
    Create incremental history entries for each wallet.
    """
    logging.info("Creating SDGCoinWallet histories...")
    for wallet in wallets:
        for _ in range(num_entries):
            increment = round(uniform(-10, 50), 2)  # Random increment between -10 and +50
            history = SDGCoinWalletHistory(
                wallet_id=wallet.sdg_coin_wallet_id,
                increment=increment,
                reason=faker.sentence(),
                is_shown=False,
                timestamp=faker.date_time_this_year(before_now=True),
            )
            session.add(history)
            logging.info(f"Created {history}.")
        # Update the wallet total after inserting histories
        wallet.total_coins = session.query(func.sum(SDGCoinWalletHistory.increment)).filter_by(wallet_id=wallet.sdg_coin_wallet_id).scalar() or 0.0
    session.commit()
    logging.info("Created wallet histories.")

def create_xp_banks(session: Session, users: list[User]):
    """
    Create SDGXPBanks for each user with SDG-specific XP values.
    """
    logging.info("Creating SDGXPBanks...")
    xp_banks = []
    for user in users:
        xp_bank = SDGXPBank(
            user_id=user.user_id,
            total_xp=0.0,  # Initialize total XP to 0.0
            sdg1_xp=round(uniform(0, 500), 2),
            sdg2_xp=round(uniform(0, 500), 2),
            sdg3_xp=round(uniform(0, 500), 2),
            sdg4_xp=round(uniform(0, 500), 2),
            sdg5_xp=round(uniform(0, 500), 2),
            sdg6_xp=round(uniform(0, 500), 2),
            sdg7_xp=round(uniform(0, 500), 2),
            sdg8_xp=round(uniform(0, 500), 2),
            sdg9_xp=round(uniform(0, 500), 2),
            sdg10_xp=round(uniform(0, 500), 2),
            sdg11_xp=round(uniform(0, 500), 2),
            sdg12_xp=round(uniform(0, 500), 2),
            sdg13_xp=round(uniform(0, 500), 2),
            sdg14_xp=round(uniform(0, 500), 2),
            sdg15_xp=round(uniform(0, 500), 2),
            sdg16_xp=round(uniform(0, 500), 2),
            sdg17_xp=round(uniform(0, 500), 2),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )
        # Calculate the total XP as the sum of SDG-specific XP values
        xp_bank.total_xp = sum(
            getattr(xp_bank, f"sdg{i}_xp") for i in range(1, 18)
        )
        session.add(xp_bank)
        logging.info(f"Created {xp_bank}.")
        xp_banks.append(xp_bank)
    session.commit()
    logging.info(f"Created {len(xp_banks)} SDGXPBanks.")
    return xp_banks


def create_xp_bank_histories(session: Session, xp_banks: list[SDGXPBank], num_entries: int = 5):
    """
    Create incremental history entries for each XP bank with SDG-specific increments.
    """
    logging.info("Creating SDGXPBank histories...")

    # Define valid SDG types (excluding SDG_0 and SDG_18)
    valid_sdg_types = [sdg for sdg in SDGType if sdg.value not in {"sdg0", "sdg18"}]

    for xp_bank in xp_banks:
        for _ in range(num_entries):
            # Randomly choose a valid SDG to update
            sdg = choice(valid_sdg_types)

            increment = round(uniform(10, 100), 2)  # Random increment between +10 and +100
            history = SDGXPBankHistory(
                xp_bank_id=xp_bank.sdg_xp_bank_id,
                sdg=sdg,
                increment=increment,
                reason=faker.sentence(),
                is_shown=False,
                timestamp=faker.date_time_this_year(before_now=True),
            )
            session.add(history)
            logging.info(f"Created {history}.")
            # Update the specific SDG XP field and total XP
            sdg_field = f"{sdg.value.lower()}_xp"
            if hasattr(xp_bank, sdg_field):
                current_value = getattr(xp_bank, sdg_field, 0.0)
                setattr(xp_bank, sdg_field, max(0.0, current_value + increment))  # Ensure no negative XP
            xp_bank.total_xp = sum(
                getattr(xp_bank, f"sdg{i}_xp") for i in range(1, 18)
            )
    session.commit()
    logging.info("Created XP bank histories.")

def create_votes_for_annotations(session: Session, annotations: list[Annotation], users: list[User], num_votes: int = 20):
    """
    Create Votes attached to Annotations and store them in the database.
    """
    logging.info("Creating Votes for Annotations...")
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
            created_at=faker.date_time_this_year(before_now=True),
        )

        session.add(vote)
        logging.info(f"Created {vote}.")
        votes.append(vote)
    session.commit()
    logging.info(f"Created {len(votes)} Votes for Annotations.")
    return votes

def create_sdg_label_decisions_for_scenarios(
    session: Session, publications: List[Publication], experts: List[Expert], users: List[User],
):
    """
    Create SDGLabelDecisions for publications based on scenarios and ground truth data.
    Ensure the label distribution is appropriate for each scenario.
    """
    logging.info("Creating SDGLabelDecisions for scenarios...")
    decisions = []

    # Assign temporary personas
    user_personas = assign_personas(users)  # In-memory mapping, no DB change

    # Define all possible SDGs (excluding SDG0 and SDG18)
    all_sdgs = [f"SDG{i}" for i in range(1, 18)]

    for publication in publications:
        if not publication or publication.publication_id is None:
            logging.error(f"No valid publication found! Skipping this scenario.")
            continue  # Skip if no valid publication

        sdg_label_summary = publication.sdg_label_summary
        if not sdg_label_summary:
            logging.warning(f"No SDGLabelSummary found for publication ID {publication.publication_id}. Skipping.")
            continue

        # Determine the true SDG label (the one set to 1)
        true_sdg = next((f"SDG{i}" for i in range(1, 18) if getattr(sdg_label_summary, f"sdg{i}") == 1), None)
        if not true_sdg:
            logging.warning(f"No true SDG label found for publication ID {publication.publication_id}. Skipping.")
            continue

        logging.info(f"True SDG for publication ID {publication.publication_id}: {true_sdg}")

        # Define non-relevant SDGs (all SDGs except the true one)
        non_relevant_sdgs = [sdg for sdg in all_sdgs if sdg != true_sdg]
        logging.debug(f"Non-relevant SDGs for publication ID {publication.publication_id}: {non_relevant_sdgs}")

        expert = choice(experts)
        scenario = choice(list(ScenarioType)[:-2])  # Exclude last two scenarios

        logging.debug(f"Selected scenario for publication ID {publication.publication_id}: {scenario}")

        # Initialize labels list
        labels = []

        # Determine the label distribution based on the scenario
        if scenario == ScenarioType.CONFIRM:
            # Clear majority (e.g., 90% majority)
            majority_count = int(fixtures_settings.VOTES_NEEDED_FOR_SCENARIO * fixtures_settings.CONFIRM_MAJORITY_RATIO)
            minority_count = fixtures_settings.VOTES_NEEDED_FOR_SCENARIO - majority_count
            majority_label = true_sdg  # Always use the true SDG as the majority label
            minority_label = choice(non_relevant_sdgs)  # Choose a non-relevant SDG as the minority label
            logging.debug(f"Majority Count: {majority_count}, Minority Count: {minority_count}")
            logging.debug(f"Majority Label: {majority_label}, Minority Label: {minority_label}")
            labels = [majority_label] * majority_count + [minority_label] * minority_count

        elif scenario == ScenarioType.TIEBREAKER:
            # Close split (e.g., 50-50)
            split_count = int(fixtures_settings.VOTES_NEEDED_FOR_SCENARIO * fixtures_settings.TIEBREAKER_RATIO)
            label1 = true_sdg  # Always include the true SDG
            label2 = choice(non_relevant_sdgs)  # Choose a non-relevant SDG
            logging.debug(f"Split Count: {split_count}")
            logging.debug(f"Label 1: {label1}, Label 2: {label2}")
            labels = [label1] * split_count + [label2] * split_count

        elif scenario == ScenarioType.INVESTIGATE:
            # Complex distribution (e.g., 3/3/3/1)
            # Ensure the true SDG is always included
            labels = [true_sdg] * fixtures_settings.INVESTIGATE_DISTRIBUTION[0]  # First group is the true SDG
            # Add non-relevant SDGs for the remaining groups
            for count in fixtures_settings.INVESTIGATE_DISTRIBUTION[1:]:
                labels.extend([choice(non_relevant_sdgs)] * count)
            logging.debug(f"Labels: {labels}")

        elif scenario == ScenarioType.EXPLORE:
            # Diverse distribution (e.g., 1/2/2/2/1/1/1)
            # Ensure the true SDG is always included
            labels = [true_sdg] * fixtures_settings.EXPLORE_DISTRIBUTION[0]  # First group is the true SDG
            # Add non-relevant SDGs for the remaining groups
            for count in fixtures_settings.EXPLORE_DISTRIBUTION[1:]:
                labels.extend([choice(non_relevant_sdgs)] * count)
            logging.debug(f"Labels: {labels}")

        elif scenario == ScenarioType.NO_SPECIFIC_SCENARIO:
            # Default to a random distribution, but always include the true SDG
            labels = [true_sdg] * (fixtures_settings.VOTES_NEEDED_FOR_SCENARIO // 2)  # Half are the true SDG
            labels.extend([choice(non_relevant_sdgs) for _ in range(fixtures_settings.VOTES_NEEDED_FOR_SCENARIO // 2)])
            logging.debug(f"Labels: {labels}")

        else:
            logging.error(f"Unknown scenario type: {scenario}. Skipping.")
            continue

        logging.debug(f"Labels for publication ID {publication.publication_id} and scenario {scenario}: {labels}")

        # Ensure labels list is not empty
        if not labels:
            logging.error(f"No labels generated for publication ID {publication.publication_id} and scenario {scenario}. Skipping.")
            continue

        # Extract the SDG number from the true_sdg (e.g., "SDG12" -> 12)
        true_sdg_number = int(true_sdg[3:])  # Extract the number after "SDG"

        # Step 1: Create SDGLabelDecision
        # Create a decision based on the scenario and label distribution

        user = choice(users)
        persona_data = user_personas.get(user.user_id, {})

        if not persona_data:
            logging.warning(f"No persona found for user {user.user_id}, using default decision comment.")
            decision_comment = "This decision is based on majority consensus and current SDG alignment."
        else:
            try:
                # Generate Persona-Based Decision Comment using GPT Service
                response = gpt_service.generate_comment(
                    abstract=publication.description,  # Ensure publication has a valid description
                    persona=persona_data["persona"].value,
                    interest=persona_data["interest"],
                    skill=persona_data["skill"],
                    trust_score=persona_data["trust_score"]
                )
                decision_comment = response.comment_text  # Use AI-generated comment

            except Exception as e:
                logging.error(f"Error generating SDGLabelDecision comment for user {user.user_id}: {e}")
                decision_comment = "This decision is based on majority consensus and current SDG alignment."

        # Create a decision based on the scenario and label distribution
        decision = SDGLabelDecision(
            history_id=sdg_label_summary.history_id,
            expert_id=None,  # No expert, only users are used
            publication_id=publication.publication_id,
            suggested_label=true_sdg_number,  # Use the integer value of the true SDG
            decided_label=0,  # Set decided label to 0 (not yet decided)
            decision_type=DecisionType.CONSENSUS_MAJORITY,
            scenario_type=scenario,
            comment=decision_comment,  # Use AI-generated comment
            decided_at=datetime.now(),
            created_at=faker.date_time_this_year(before_now=True),
            updated_at=faker.date_time_this_year(before_now=True),
        )

        session.add(decision)
        session.commit()  # Commit the decision
        logging.info(f"Created SDGLabelDecision {decision} for scenario {scenario}.")

        # Step 2: Create SDGUserLabels
        user_labels = []
        selected_users = set()  # A set to keep track of already selected users

        for label in labels:
            sdg_number = int(label[3:])

            # Find a user who hasn't been selected yet
            available_users = [user for user in users if user.user_id not in selected_users]

            if not available_users:
                logging.warning(f"No more unique users available for SDGLabel {sdg_number}. Skipping label.")
                continue  # Skip this label if no more unique users are available

            user = choice(available_users)  # Select a random user from available users
            selected_users.add(user.user_id)  # Mark this user as selected

            persona_data = user_personas.get(user.user_id, {})

            if not persona_data:
                logging.warning(f"No persona found for user {user.user_id}, using default values.")
                abstract_section = "General observation on SDG impact."
                comment = "No specific insights provided."
            else:
                try:
                    # Generate Persona-Based Abstract Section & Comment using GPT Service
                    response = gpt_service.generate_comment(
                        abstract=publication.description,  # Ensure publication has a valid description
                        persona=persona_data["persona"].value,
                        interest=persona_data["interest"],
                        skill=persona_data["skill"],
                        trust_score=persona_data["trust_score"]
                    )
                    logging.debug(response)

                    abstract_section = response.abstract_section
                    comment = response.comment_text  # Use AI-generated comment

                except Exception as e:
                    logging.error(f"Error generating SDGUserLabel content for user {user.user_id}: {e}")
                    abstract_section = "General observation on SDG impact."
                    comment = "No specific insights provided."

            user_label = SDGUserLabel(
                user_id=user.user_id,
                proposed_label=sdg_number,
                voted_label=sdg_number,
                publication_id=publication.publication_id,
                abstract_section=abstract_section,
                comment=comment,
                labeled_at=datetime.now(),
                created_at=faker.date_time_this_year(before_now=True),
                updated_at=faker.date_time_this_year(before_now=True),
            )
            decision.user_labels.append(user_label)
            session.add(user_label)
            user_labels.append(user_label)

        session.commit()
        logging.info(f"Created {len(user_labels)} SDGUserLabels for decision {decision.decision_id}.")

        # Step 3: Generate Persona-Based Annotations using Temporary Personas
        annotations = []

        for user_label in user_labels:
            persona_data = user_personas.get(user_label.user_id, {})

            if not persona_data:
                continue

            try:
                response = gpt_service.generate_annotation(
                    abstract=publication.description,
                    persona=persona_data["persona"].value,
                    interest=persona_data["interest"],
                    skill=persona_data["skill"],
                    trust_score=persona_data["trust_score"],
                    user_label_comment=user_label.comment
                )
                logging.debug(response)

                annotation = Annotation(
                    user_id=user_label.user_id,
                    sdg_user_label_id=user_label.label_id,
                    decision_id=None,
                    labeler_score=round(uniform(1.0, 100.0), 2),
                    comment=response.annotation_text,
                    created_at=faker.date_time_this_year(before_now=True),
                    updated_at=faker.date_time_this_year(before_now=True),
                )
                session.add(annotation)
                annotations.append(annotation)

            except Exception as e:
                logging.error(f"Error generating annotation for user {user_label.user_id}: {e}")

        # Step 3B: Generate Annotations Linked to Decision
        for _ in range(randint(1, 3)):
            user = choice(users)
            persona_data = user_personas.get(user.user_id, {})

            if not persona_data:
                continue

            try:
                response = gpt_service.generate_annotation(
                    abstract=publication.description,
                    persona=persona_data["persona"].value,
                    interest=persona_data["interest"],
                    skill=persona_data["skill"],
                    trust_score=persona_data["trust_score"],
                    decision_comment=decision.comment
                )
                logging.debug(response)

                annotation = Annotation(
                    user_id=user.user_id,
                    sdg_user_label_id=None,
                    decision_id=decision.decision_id,
                    labeler_score=round(uniform(1.0, 100.0), 2),
                    comment=response.annotation_text,
                    created_at=faker.date_time_this_year(before_now=True),
                    updated_at=faker.date_time_this_year(before_now=True),
                )
                session.add(annotation)
                annotations.append(annotation)

            except Exception as e:
                logging.error(f"Error generating annotation for decision {decision.decision_id}: {e}")

        session.commit()
        logging.info(f"Created {len(annotations)} persona-based annotations for decision {decision.decision_id}.")

        # Step 4: Create Votes
        for user_label in user_labels:
            for _ in range(randint(1, 5)):
                vote = Vote(
                    user_id=choice(users).user_id,
                    sdg_user_label_id=user_label.label_id,
                    annotation_id=None,
                    vote_type=choice(list(VoteType)),
                    score=round(uniform(0, 5), 2),
                    created_at=faker.date_time_this_year(before_now=True),
                )
                session.add(vote)
        for annotation in annotations:
            for _ in range(randint(1, 5)):
                vote = Vote(
                    user_id=choice(users).user_id,
                    sdg_user_label_id=None,
                    annotation_id=annotation.annotation_id,
                    vote_type=choice(list(VoteType)),
                    score=round(uniform(0, 5), 2),
                    created_at=faker.date_time_this_year(before_now=True),
                )
                session.add(vote)
        session.commit()

    logging.info("Completed creating SDGLabelDecisions for scenarios.")
    return decisions


def populate_db(
    session: Session,
    truncate: bool = False,
    max_users: int = 100,
    history_entries_per_user: int = 5,
    max_pubs: int = 5,
    num_labels: int = 4,
    num_votes: int = 10,
    num_annotations: int = 5,
    num_decisions: int = 4,
):
    """
    Populate the database with fixtures for SDGUserLabel, Vote, Annotation, SDGLabelDecision, SDGCoinWallet and SDGXPBanks.
    Optionally truncates the relevant tables before insertion.
    """
    try:
        # Truncate tables if the flag is set
        if truncate:
            truncate_tables(session, ["sdg_user_labels", "votes", "annotations", "sdg_label_decisions", "sdg_label_decision_user_label", "sdg_coin_wallets", "sdg_xp_banks"])

        # Load users, user_personas, publications, and experts
        users = load_users(session, max_users)
        user_personas = assign_personas(users)  # Store the temporary mapping
        publications = load_publications(session, max_pubs)
        experts = load_experts(session)

        if not users or not publications or not experts:
            logging.error("Users, Publications, or Experts not found in the database. Exiting.")
            return

        # Fetch existing SDGLabelHistories
        histories = session.query(SDGLabelHistory).all()
        if not histories:
            logging.error("No SDGLabelHistories found in the database.")
            return

        # Create wallets and XP banks for each user
        wallets = create_wallets(session, users)
        xp_banks = create_xp_banks(session, users)

        # Create histories for wallets and XP banks
        create_wallet_histories(session, wallets, num_entries=history_entries_per_user)
        create_xp_bank_histories(session, xp_banks, num_entries=history_entries_per_user)

        if False:
            # Create SDGUserLabels
            user_labels = create_sdg_user_labels(session, users, publications, num_labels)

            # Create Votes
            create_votes(session, users, user_labels, num_votes)

            # Create Annotations
            create_annotations(session, users, user_labels, num_annotations)

            # Create Votes for Annotations
            annotations = create_annotations(session, users, user_labels, num_annotations)
            create_votes_for_annotations(session, annotations, users, num_votes)

            # Create SDGLabelDecisions
            create_sdg_label_decisions(session, histories, user_labels, experts, publications, num_decisions)


        # Create scenario-based decisions
        relevant_publications = load_relevant_publications_with_sdg_labels(session, max_pubs=500)

        create_sdg_label_decisions_for_scenarios(
            session,
            publications=relevant_publications,
            experts=experts,
            users=users,
        )

        logging.info("Database population completed successfully.")

    except IntegrityError as e:
        session.rollback()
        logging.error(f"IntegrityError encountered: {e}")

    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred during database population: {e}")


if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=mariadb_engine)

    # Ensure tables are created
    Base.metadata.create_all(mariadb_engine)

    with Session() as session:
        populate_db(session, truncate=True)

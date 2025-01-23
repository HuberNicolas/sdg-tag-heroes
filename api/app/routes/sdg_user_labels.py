from collections import Counter
from datetime import datetime
from typing import List
import re
from random import choice

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine


from models import SDGUserLabel, SDGLabelDecision, sdg_label_decision_user_label_association, SDGPrediction, Vote, \
    SDGCoinWalletHistory, SDGCoinWallet
from models.publications.publication import Publication
from models.sdg_label_decision import DecisionType
from models.sdg_label_history import SDGLabelHistory
from models.sdg_label_summary import SDGLabelSummary
from schemas import SDGUserLabelSchemaFull, SDGUserLabelSchemaBase
from schemas.vote import VoteSchemaFull
from settings.settings import SDGUserLabelsSettings
from utils.logger import logger

# Setup Logging
sdg_user_labels_router_settings = SDGUserLabelsSettings()
logging = logger(sdg_user_labels_router_settings.SDGUSERLABELS_ROUTER_LOG_NAME)

# Setup OAuth2 and security
security = Security()
oauth2_scheme = security.oauth2_scheme

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create the API router
router = APIRouter(
    prefix="/user-labels",
    tags=["User Labels"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get(
    "/{label_id}",
    response_model=SDGUserLabelSchemaFull,
    description="Retrieve a specific SDG user label by ID"
)
async def get_sdg_user_label(
    label_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGUserLabelSchemaFull:
    """
    Retrieve a specific SDG user label by its ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        user_label = db.query(SDGUserLabel).filter(SDGUserLabel.label_id == label_id).first()

        if not user_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDG user label with ID {label_id} not found",
            )

        return SDGUserLabelSchemaFull.model_validate(user_label)

    except Exception as e:
        logging.error(f"Error fetching SDG user label ID {label_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDG user label",
        )

@router.get(
    "/",
    response_model=List[SDGUserLabelSchemaFull],
    description="Retrieve all SDG user labels"
)
async def get_all_sdg_user_labels(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGUserLabelSchemaFull]:
    """
    Retrieve all SDG user labels in the system.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        user_labels = db.query(SDGUserLabel).all()
        return [SDGUserLabelSchemaFull.model_validate(label) for label in user_labels]

    except Exception as e:
        logging.error(f"Error fetching SDG user labels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG user labels",
        )


@router.get(
    "/publications/{publication_id}/",
    response_model=List[SDGUserLabelSchemaFull],
    description="Retrieve all SDG user labels for a specific publication.",
)
async def get_sdg_user_labels_for_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGUserLabelSchemaFull]:
    """
    Retrieve all SDG user labels associated with a specific publication.
    """
    try:
        verify_token(token, db)  # Ensure user is authenticated


        # Retrieve the publication with its associated SDGLabelSummary and SDGLabelHistory
        publication = db.query(Publication).options(
            joinedload(Publication.sdg_label_summary).joinedload(SDGLabelSummary.history)
        ).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found.",
            )

        if not publication.sdg_label_summary or not publication.sdg_label_summary.history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelSummary or SDGLabelHistory for Publication ID {publication_id} not found.",
            )

        history = publication.sdg_label_summary.history

        # Retrieve all SDGUserLabels and their related entities in a single query
        labels = db.query(SDGUserLabel).options(
            joinedload(SDGUserLabel.votes),
            joinedload(SDGUserLabel.annotations),
            joinedload(SDGUserLabel.label_decisions),
        ).join(
            sdg_label_decision_user_label_association,
            sdg_label_decision_user_label_association.c.user_label_id == SDGUserLabel.label_id
        ).join(
            SDGLabelDecision,
            sdg_label_decision_user_label_association.c.decision_id == SDGLabelDecision.decision_id
        ).filter(
            SDGLabelDecision.history_id == history.history_id
        ).all()

        # Convert SQLAlchemy models to Pydantic models
        return [SDGUserLabelSchemaFull.model_validate(label) for label in labels]

    except HTTPException as he:
        raise he  # Re-raise HTTPException to return specific error responses
    except Exception as e:
        logging.error(f"Error retrieving SDG user labels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving SDG user labels.",
        )


@router.get(
    "/{label_id}/votes/{vote_id}",
    response_model=VoteSchemaFull,
    description="Retrieve a specific vote associated with a specific SDG user label"
)
async def get_vote_for_sdg_user_label(
    label_id: int,
    vote_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> VoteSchemaFull:
    """
    Retrieve a specific vote associated with a specific SDG user label.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Directly query the Vote table with both label_id and vote_id
        vote = db.query(Vote).filter(
            Vote.sdg_user_label_id == label_id,
            Vote.vote_id == vote_id
        ).first()

        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vote with ID {vote_id} not found for SDG user label ID {label_id}",
            )

        return VoteSchemaFull.model_validate(vote)

    except HTTPException as he:
        raise he  # Re-raise HTTPException to return specific error responses
    except Exception as e:
        logging.error(f"Error fetching vote ID {vote_id} for SDG user label ID {label_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the vote for the SDG user label",
        )


@router.get(
    "/{label_id}/votes",
    response_model=List[VoteSchemaFull],
    description="Retrieve all votes associated with a specific SDG user label"
)
async def get_votes_for_sdg_user_label(
    label_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[VoteSchemaFull]:
    """
    Retrieve all votes associated with a specific SDG user label.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        sdg_user_label = db.query(SDGUserLabel).filter(SDGUserLabel.label_id == label_id).first()
        if not sdg_user_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDG user label with ID {label_id} not found",
            )

        return [VoteSchemaFull.model_validate(vote) for vote in sdg_user_label.votes]

    except Exception as e:
        logging.error(f"Error fetching votes for SDG user label ID {label_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching votes for the SDG user label",
        )

@router.get(
    "/label_decisions/{decision_id}/",
    response_model=List[SDGUserLabelSchemaBase],
    description="Retrieve all SDGUserLabel entries associated with a specific SDGLabelDecision"
)
async def get_sdg_user_labels(
    decision_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGUserLabelSchemaBase]:
    """
    Retrieve all SDGUserLabel entries for a specific SDGLabelDecision.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the SDGLabelDecision with its associated user_labels
        decision = (
            db.query(SDGLabelDecision)
            .options(joinedload(SDGLabelDecision.user_labels))  # Eager load user_labels
            .filter(SDGLabelDecision.decision_id == decision_id)
            .first()
        )

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found",
            )

        # Return the list of SDGUserLabels associated with the decision
        return [SDGUserLabelSchemaBase.model_validate(label) for label in decision.user_labels]

    except HTTPException as he:
        raise he  # Re-raise HTTPException to return specific error responses
    except Exception as e:
        logging.error(f"Error fetching SDGUserLabels for decision ID {decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDGUserLabels for the decision",
        )

@router.get(
    "/label_decisions/{decision_id}/{label_id}",
    response_model=SDGUserLabelSchemaFull,
    description="Retrieve a specific SDGUserLabel entry associated with a specific SDGLabelDecision"
)
async def get_sdg_user_label(
    decision_id: int,
    label_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGUserLabelSchemaFull:
    """
    Retrieve a specific SDGUserLabel entry for a specific SDGLabelDecision.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the SDGLabelDecision with its associated user_labels
        decision = (
            db.query(SDGLabelDecision)
            .options(joinedload(SDGLabelDecision.user_labels))  # Eager load user_labels
            .filter(SDGLabelDecision.decision_id == decision_id)
            .first()
        )

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found",
            )

        # Check if the SDGUserLabel is associated with the decision
        label = next((l for l in decision.user_labels if l.label_id == label_id), None)

        if not label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGUserLabel with ID {label_id} not associated with decision ID {decision_id}",
            )

        return SDGUserLabelSchemaFull.model_validate(label)

    except HTTPException as he:
        raise he  # Re-raise HTTPException to return specific error responses
    except Exception as e:
        logging.error(f"Error fetching SDGUserLabel ID {label_id} for decision ID {decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGUserLabel for the decision",
        )

if False:
    @router.post(
        "/",
        response_model=SDGUserLabelSchemaFull,
        description="Create or link an SDG user label"
    )
    async def create_sdg_user_label(
            user_label_data: SDGUserLabelSchemaCreate,
            db: Session = Depends(get_db),
            token: str = Depends(oauth2_scheme),
    ) -> SDGUserLabelSchemaFull:
        """
        Create or link an SDG user label.
        """
        try:
            user = verify_token(token, db)  # Ensure user is authenticated
            decision = None

            # Link to an existing SDGLabelDecision
            if user_label_data.decision_id:
                decision = db.query(SDGLabelDecision).filter(
                    SDGLabelDecision.decision_id == user_label_data.decision_id).first()
                if not decision:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"SDGLabelDecision with ID {user_label_data.decision_id} not found",
                    )
            else:
                # Ensure `publication_id` is provided
                if not user_label_data.publication_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Either publication_id or history_id must be provided to create a new SDGLabelDecision",
                    )

                # Fetch publication and associated history
                publication = db.query(Publication).filter(
                    Publication.publication_id == user_label_data.publication_id).first()
                if not publication:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Publication with ID {user_label_data.publication_id} not found",
                    )

                sdg_label_summary = db.query(SDGLabelSummary).filter(
                    SDGLabelSummary.publication_id == publication.publication_id).first()
                if not sdg_label_summary:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="SDGLabelSummary not found for the given publication",
                    )
                history = db.query(SDGLabelHistory).filter(
                    SDGLabelHistory.history_id == sdg_label_summary.history_id).first()
                if not history:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="SDGLabelHistory not found for the given summary",
                    )

                sdg_prediction = db.query(SDGPrediction).filter(
                    SDGPrediction.publication_id == publication.publication_id and SDGPrediction.prediction_model == "Aurora").first()

                if sdg_prediction:
                    highest_sdg = sdg_prediction.get_highest_sdg()
                    highest_sdg_number = re.findall(r'\d+', highest_sdg[0])[0]
                    print(f"Highest SDG: {highest_sdg[0]}, (number: {highest_sdg_number}) with value {highest_sdg[1]}")

                if sdg_prediction:
                    sdgs_above_threshold = sdg_prediction.get_sdgs_above_threshold(threshold=0.98)
                    print("SDGs above threshold:")
                    for sdg, value in sdgs_above_threshold.items():
                        print(f"{sdg}: {value}")

                print(history)
                # Find an unfinished decision or create a new one
                if len(history.decisions) == 0:
                    # Create a new SDGLabelDecision
                    decision = SDGLabelDecision(
                        suggested_label=highest_sdg_number,
                        history_id=history.history_id,
                        decision_type=user_label_data.decision_type,
                        decided_at=datetime.now(),
                    )
                    db.add(decision)
                    db.flush()  # Ensure the decision is persisted before associating it
                else:
                    unfinished_decision = next((d for d in history.decisions if d.decided_label == -1), None)

                    if unfinished_decision == None:
                        # Create a new SDGLabelDecision
                        decision = SDGLabelDecision(
                            suggested_label=highest_sdg_number,
                            history_id=history.history_id,
                            decision_type=user_label_data.decision_type,
                            decided_at=datetime.now(),
                        )
                        db.add(decision)
                        db.flush()  # Ensure the decision is persisted before associating it
                    else:
                        decision = unfinished_decision
            print(user_label_data)
            print(user_label_data.abstract_section)
            # Create the new SDG user label
            new_user_label = SDGUserLabel(
                user_id=user["user_id"],
                #proposed_label=highest_sdg_number,  # Nullable, TODO: load from world
                voted_label=user_label_data.voted_label,  # Required
                abstract_section=user_label_data.abstract_section or "",  # Default to empty string
                comment=user_label_data.comment or "",  # Default to empty string
            )
            db.add(new_user_label)
            db.flush()  # Persist the new_user_label to get its ID


            print(decision)
            # Associate the user label with the decision
            decision.user_labels.append(new_user_label)

            # Decision logic: Calculate based on current user labels
            # Group labels by user
            user_votes = {}
            for label in decision.user_labels:
                if label.user_id not in user_votes:
                    user_votes[label.user_id] = set()
                user_votes[label.user_id].add(label.voted_label)  # Add to the set for unique SDGs per user
                print(user_votes)


            if len(user_votes) >= 3:  # At least 3 distinct users
                print("Decision")
                # Aggregate votes across all users
                aggregated_votes = Counter()
                for user_set in user_votes.values():
                    aggregated_votes.update(user_set)  # Count each SDG in the user's set

                # Determine majority
                max_votes = max(aggregated_votes.values())
                most_voted_labels = [label for label, count in aggregated_votes.items() if count == max_votes]

                if len(most_voted_labels) > 1:
                    # Tie: Randomly decide among tied labels
                    decision.decided_label = choice(most_voted_labels)
                else:
                    # Clear majority
                    decision.decided_label = most_voted_labels[0]

                decision.decision_type = DecisionType.CONSENSUS_MAJORITY
                decision.decided_at = datetime.now()
            else:
                print("No decision")
                # Not enough distinct users for consensus, leave decision undecided (-1)
                decision.decided_label = -1
                decision.decision_type = DecisionType.CONSENSUS_MAJORITY

            # Update history if a decision is finalized
            if decision.decided_label != -1:
                if not decision.history:
                    decision.history = SDGLabelHistory(
                        active=True,
                        created_at=datetime.now(),
                    )
                decision.history.updated_at = datetime.now()

            # Reward logic for users
            winning_label = decision.decided_label
            winners = []
            for user_id, user_set in user_votes.items():
                if winning_label in user_set:
                    winners.append(user_id)

            for user_id in user_votes:
                wallet = db.query(SDGCoinWallet).filter(SDGCoinWallet.user_id == user_id).first()
                if not wallet:
                    print(f"Wallet for user {user_id} not found. Skipping rewards.")
                    continue

                # Apply reward logic
                if user_id in winners:
                    # Winner logic: Max 3 SDG labels result in +100 coins
                    if len(user_votes[user_id]) <= 3:
                        increment = 100
                        reason = f"Reward for voting for SDG {winning_label}."
                    else:
                        # Penalty for voting on too many SDGs
                        increment = -10 * (len(user_votes[user_id]) - 3)
                        reason = f"Penalty for voting on too many SDGs (limit 3)."
                else:
                    # No reward for users not voting for the winning SDG
                    increment = 0
                    reason = f"No reward: Did not vote for SDG {winning_label}."

                # Update wallet and add history
                if increment != 0:
                    wallet.total_coins += increment
                    wallet_history = SDGCoinWalletHistory(
                        wallet_id=wallet.sdg_coin_wallet_id,
                        increment=increment,
                        reason=reason,
                    )
                    db.add(wallet_history)

            # Update summary with the latest decision
            if decision.history and decision.history.label_summary:
                summary = decision.history.label_summary
                print(summary)
                decided_sdg_field = f"sdg{decision.decided_label}"
                current_value = getattr(summary, decided_sdg_field, 0)
                if current_value == 0:  # Update only if it's currently 0
                    setattr(summary, decided_sdg_field, 1)
                print(summary)

            # Commit the transaction
            db.commit()
            db.refresh(new_user_label)

            return SDGUserLabelSchemaFull.model_validate(new_user_label)

        except Exception as e:
            logging.error(f"Error creating or linking SDG user label: {str(e)}")
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating or linking the SDG user label",
            )


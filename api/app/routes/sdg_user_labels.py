from datetime import datetime
from typing import List
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine


from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import SDGUserLabel, SDGLabelDecision, sdg_label_decision_user_label_association, SDGPrediction, Vote
from models.publications.publication import Publication
from models.sdg_label_history import SDGLabelHistory
from models.sdg_label_summary import SDGLabelSummary
from schemas.sdg_user_label import SDGUserLabelSchemaFull, SDGUserLabelSchemaCreate
from schemas.vote import VoteSchemaFull
from settings.settings import SDGUserLabelsSettings
sdg_user_labels_router_settings = SDGUserLabelsSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(sdg_user_labels_router_settings.SDGUSERLABELS_ROUTER_LOG_NAME)


router = APIRouter(
    prefix="/sdg_user_labels",
    tags=["sdg_user_labels"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/publications/{publication_id}/labels",
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
        # Verify token (optional, depending on access control requirements)
        verify_token(token, db)

        # Retrieve the publication
        publication = db.query(Publication).filter(
            Publication.publication_id == publication_id
        ).first()
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found.",
            )


        # Retrieve associated SDGLabelSummary
        sdg_label_summary = db.query(SDGLabelSummary).filter(
            SDGLabelSummary.publication_id == publication.publication_id
        ).first()
        if not sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelSummary for Publication ID {publication.publication_id} not found.",
            )


        # Retrieve associated SDGLabelHistory
        history = db.query(SDGLabelHistory).filter(
            SDGLabelHistory.history_id == sdg_label_summary.history_id
        ).first()
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelHistory for Summary ID {sdg_label_summary.sdg_label_summary_id} not found.",
            )

        # Retrieve all SDGUserLabels through the association table
        labels = (
            db.query(SDGUserLabel)
            .join(sdg_label_decision_user_label_association,
                  sdg_label_decision_user_label_association.c.user_label_id == SDGUserLabel.label_id)
            .join(SDGLabelDecision,
                  sdg_label_decision_user_label_association.c.decision_id == SDGLabelDecision.decision_id)
            .filter(SDGLabelDecision.history_id == history.history_id)
            .all()
        )

        # Fetch votes for each label and add to the result
        result = []
        for label in labels:
            label_dict = SDGUserLabelSchemaFull.model_validate(label).dict()
            # Fetch votes for the label
            votes = db.query(Vote).filter(Vote.sdg_user_label_id == label.label_id).all()
            label_dict["votes"] = [VoteSchemaFull.model_validate(vote).dict() for vote in votes]
            result.append(label_dict)
        print(result)

        return result

    except Exception as e:
        logging.error(f"Error retrieving SDG user labels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving SDG user labels.",
        )


@router.get(
    "/{sdg_user_label_id}/votes/{vote_id}",
    response_model=VoteSchemaFull,
    description="Retrieve a specific vote associated with a specific SDG user label"
)
async def get_vote_for_sdg_user_label(
    sdg_user_label_id: int,
    vote_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> VoteSchemaFull:
    """
    Retrieve a specific vote associated with a specific SDG user label.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        sdg_user_label = db.query(SDGUserLabel).filter(SDGUserLabel.label_id == sdg_user_label_id).first()
        if not sdg_user_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDG user label with ID {sdg_user_label_id} not found",
            )

        vote = next((vote for vote in sdg_user_label.votes if vote.vote_id == vote_id), None)
        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vote with ID {vote_id} not found for SDG user label ID {sdg_user_label_id}",
            )

        return VoteSchemaFull.model_validate(vote)

    except Exception as e:
        logging.error(f"Error fetching vote ID {vote_id} for SDG user label ID {sdg_user_label_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the vote for the SDG user label",
        )


@router.get(
    "/{sdg_user_label_id}/votes",
    response_model=List[VoteSchemaFull],
    description="Retrieve all votes associated with a specific SDG user label"
)
async def get_votes_for_sdg_user_label(
    sdg_user_label_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[VoteSchemaFull]:
    """
    Retrieve all votes associated with a specific SDG user label.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        sdg_user_label = db.query(SDGUserLabel).filter(SDGUserLabel.label_id == sdg_user_label_id).first()
        if not sdg_user_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDG user label with ID {sdg_user_label_id} not found",
            )

        return [VoteSchemaFull.model_validate(vote) for vote in sdg_user_label.votes]

    except Exception as e:
        logging.error(f"Error fetching votes for SDG user label ID {sdg_user_label_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching votes for the SDG user label",
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
            print(publication)

            sdg_label_summary = db.query(SDGLabelSummary).filter(
                SDGLabelSummary.publication_id == publication.publication_id).first()
            if not sdg_label_summary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="SDGLabelSummary not found for the given publication",
                )
            print(sdg_label_summary)
            history = db.query(SDGLabelHistory).filter(
                SDGLabelHistory.history_id == sdg_label_summary.history_id).first()
            if not history:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="SDGLabelHistory not found for the given summary",
                )
            print(history)
            print(history.decisions)

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
                decision = unfinished_decision

        # Create the new SDG user label
        new_user_label = SDGUserLabel(
            user_id=user["user_id"],
            #proposed_label=highest_sdg_number,  # Nullable, TODO: load from world
            voted_label=user_label_data.voted_label,  # Required
            abstract_section=user_label_data.abstract_section or "",  # Default to empty string
            comment=user_label_data.comment or "",  # Default to empty string
        )
        print(new_user_label)
        db.add(new_user_label)
        db.flush()  # Persist the new_user_label to get its ID

        # Associate the user label with the decision
        decision.user_labels.append(new_user_label)

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
    print("Hello")
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


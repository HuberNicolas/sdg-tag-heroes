from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine
from models import Vote

from models.sdg.sdg_goal import SDGGoal

from schemas.sdg.goal import SDGGoalSchemaFull

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from schemas.vote import VoteSchemaFull, VoteSchemaCreate
from settings.settings import VotesSettings
votes_router_settings = VotesSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(votes_router_settings.VOTES_ROUTER_LOG_NAME)


router = APIRouter(
    prefix="/votes",
    tags=["votes"],
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
    "/{vote_id}",
    response_model=VoteSchemaFull,
    description="Retrieve a specific vote by ID"
)
async def get_vote(
    vote_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> VoteSchemaFull:
    """
    Retrieve a specific vote by its ID.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        vote = db.query(Vote).filter(Vote.vote_id == vote_id).first()

        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vote with ID {vote_id} not found",
            )

        return VoteSchemaFull.model_validate(vote)

    except Exception as e:
        logging.error(f"Error fetching vote ID {vote_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the vote",
        )


@router.post(
    "/",
    response_model=VoteSchemaFull,
    description="Create a new vote"
)
async def create_vote(
    vote_data: VoteSchemaCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> VoteSchemaFull:
    """
    Create a new vote.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        # Ensure that exactly one of `sdg_user_label_id` or `annotation_id` is provided
        if (vote_data.sdg_user_label_id is None) == (vote_data.annotation_id is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exactly one of sdg_user_label_id or annotation_id must be provided",
            )

        # Create the new vote
        new_vote = Vote(
            user_id=vote_data.user_id,
            sdg_user_label_id=vote_data.sdg_user_label_id,
            annotation_id=vote_data.annotation_id,
            vote_type=vote_data.vote_type,
            score=vote_data.score,
        )

        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)

        return VoteSchemaFull.model_validate(new_vote)

    except Exception as e:
        logging.error(f"Error creating vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the vote",
        )

@router.get(
    "/",
    response_model=List[VoteSchemaFull],
    description="Retrieve all votes"
)
async def get_all_votes(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[VoteSchemaFull]:
    """
    Retrieve all votes in the system.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        votes = db.query(Vote).all()
        return [VoteSchemaFull.model_validate(vote) for vote in votes]

    except Exception as e:
        logging.error(f"Error fetching votes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching votes",
        )

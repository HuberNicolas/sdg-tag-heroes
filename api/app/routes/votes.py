from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models import Vote, SDGUserLabel, Annotation
from requests_models.vote import VoteCreateRequest
from schemas.vote import VoteSchemaFull
from settings.settings import VotesSettings
from utils.logger import logger

# Setup Logging
votes_router_settings = VotesSettings()
logging = logger(votes_router_settings.VOTES_ROUTER_LOG_NAME)

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


router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)


@router.post(
    "/",
    response_model=VoteSchemaFull,
    description="Create a new vote"
)
async def create_vote(
        request: VoteCreateRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
) -> VoteSchemaFull:
    """
    Create a new vote.
    """
    try:
        # Authenticate the user
        user = verify_token(token, db)

        # Validate that either sdg_user_label_id or annotation_id is provided, but not both
        if request.sdg_user_label_id and request.annotation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only one of sdg_user_label_id or annotation_id can be provided.",
            )
        if not request.sdg_user_label_id and not request.annotation_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either sdg_user_label_id or annotation_id must be provided.",
            )

        # Check if the SDGUserLabel or Annotation exists
        if request.sdg_user_label_id:
            sdg_user_label = db.query(SDGUserLabel).filter(
                SDGUserLabel.label_id == request.sdg_user_label_id
            ).first()
            if not sdg_user_label:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"SDGUserLabel with ID {request.sdg_user_label_id} not found.",
                )
        elif request.annotation_id:
            annotation = db.query(Annotation).filter(
                Annotation.annotation_id == request.annotation_id
            ).first()
            if not annotation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Annotation with ID {request.annotation_id} not found.",
                )

        # Create the new vote
        new_vote = Vote(
            user_id=request.user_id,
            sdg_user_label_id=request.sdg_user_label_id,
            annotation_id=request.annotation_id,
            vote_type=request.vote_type,
            score=request.score,
        )

        # Add the vote to the database
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)

        # Return the created vote
        return VoteSchemaFull.model_validate(new_vote)

    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error creating vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the vote.",
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
        user = verify_token(token, db)  # Ensure user is authenticated

        votes = db.query(Vote).all()
        return [VoteSchemaFull.model_validate(vote) for vote in votes]

    except Exception as e:
        logging.error(f"Error fetching votes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching votes",
        )


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
        user = verify_token(token, db)  # Ensure user is authenticated

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

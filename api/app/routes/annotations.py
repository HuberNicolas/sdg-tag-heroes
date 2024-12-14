from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from api.app.models.query import AnnotationScoreRequest
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import Annotation, SDGUserLabel, Vote
from schemas.annotations import AnnotationSchemaFull, AnnotationSchemaCreate
from schemas.vote import VoteSchemaFull, VoteSchemaCreate
from services.user_annotation_assessment import AnnotationScoreResponse, UserAnnotationAssessment
from settings.settings import AnnotationsSettings
annotations_router_settings = AnnotationsSettings()




security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(annotations_router_settings.ANNOTATIONS_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/annotations",
    tags=["annotations"],
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


@router.post(
    "/score",
    response_model=AnnotationScoreResponse,
    description="Evaluate an annotation against an SDG label."
)
async def evaluate_annotation_score(
    request: AnnotationScoreRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> AnnotationScoreResponse:
    """
    Evaluate an annotation's scores for relevance, depth, correctness, and creativity.
    """
    try:
        user = verify_token(token, db)  # Authenticate user

        annotation_assessment = UserAnnotationAssessment()

        # Calculate scores using the UserAnnotationAssessment class
        scores = annotation_assessment.evaluate_annotation(
            passage=request.passage,
            annotation=request.annotation,
            sdg_label=request.sdg_label
        )

        # Return the response
        return AnnotationScoreResponse(
            relevance=scores.relevance,
            depth=scores.depth,
            correctness=scores.correctness,
            creativity=scores.creativity,
            llm_score=scores.llm_score,
            semantic_score=scores.semantic_score,
            combined_score=scores.combined_score
        )
    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input. Please check your request data.",
        )
    except Exception as e:
        logging.error(f"Error evaluating annotation score: {str(e)}")
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating the annotation score.",
        )

@router.get(
    "/{annotation_id}/votes/{vote_id}",
    response_model=VoteSchemaFull,
    description="Retrieve a specific vote associated with a specific annotation"
)
async def get_vote_for_annotation(
    annotation_id: int,
    vote_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> VoteSchemaFull:
    """
    Retrieve a specific vote associated with a specific annotation.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        annotation = db.query(Annotation).filter(Annotation.annotation_id == annotation_id).first()
        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation with ID {annotation_id} not found",
            )

        vote = next((vote for vote in annotation.votes if vote.vote_id == vote_id), None)
        if not vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vote with ID {vote_id} not found for annotation ID {annotation_id}",
            )

        return VoteSchemaFull.model_validate(vote)

    except Exception as e:
        logging.error(f"Error fetching vote ID {vote_id} for annotation ID {annotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the vote for the annotation",
        )


@router.get(
    "/{annotation_id}/votes",
    response_model=List[VoteSchemaFull],
    description="Retrieve all votes associated with a specific annotation"
)
async def get_votes_for_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[VoteSchemaFull]:
    """
    Retrieve all votes associated with a specific annotation.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        annotation = db.query(Annotation).filter(Annotation.annotation_id == annotation_id).first()
        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation with ID {annotation_id} not found",
            )

        return [VoteSchemaFull.model_validate(vote) for vote in annotation.votes]

    except Exception as e:
        logging.error(f"Error fetching votes for annotation ID {annotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching votes for the annotation",
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
        user = verify_token(token, db)  # Ensure user is authenticated

        # Ensure that the validation logic in `VoteSchemaCreate` has been applied
        new_vote = Vote(
            user_id=vote_data.user_id,
            sdg_user_label_id=vote_data.sdg_user_label_id,
            annotation_id=vote_data.annotation_id,
            vote_type=vote_data.vote_type,
            score=vote_data.score,
        )

        # Check associations for existence
        if vote_data.sdg_user_label_id:
            sdg_user_label = db.query(SDGUserLabel).filter(SDGUserLabel.label_id == vote_data.sdg_user_label_id).first()
            if not sdg_user_label:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"SDGUserLabel with ID {vote_data.sdg_user_label_id} not found.",
                )
        elif vote_data.annotation_id:
            annotation = db.query(Annotation).filter(Annotation.annotation_id == vote_data.annotation_id).first()
            if not annotation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Annotation with ID {vote_data.annotation_id} not found.",
                )

        # Create the vote
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)

        return VoteSchemaFull.model_validate(new_vote)

    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        logging.error(f"Error creating vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the vote",
        )



@router.get(
    "/{annotation_id}",
    response_model=AnnotationSchemaFull,
    description="Retrieve a specific annotation by ID"
)
async def get_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> AnnotationSchemaFull:
    """
    Retrieve a specific annotation by its ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        annotation = db.query(Annotation).filter(Annotation.annotation_id == annotation_id).first()

        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Annotation with ID {annotation_id} not found",
            )

        return AnnotationSchemaFull.model_validate(annotation)

    except Exception as e:
        logging.error(f"Error fetching annotation ID {annotation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the annotation",
        )



@router.get(
    "/",
    response_model=List[AnnotationSchemaFull],
    description="Retrieve all annotations"
)
async def get_all_annotations(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[AnnotationSchemaFull]:
    """
    Retrieve all annotations in the system.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        annotations = db.query(Annotation).all()
        return [AnnotationSchemaFull.model_validate(annotation) for annotation in annotations]

    except Exception as e:
        logging.error(f"Error fetching annotations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching annotations",
        )




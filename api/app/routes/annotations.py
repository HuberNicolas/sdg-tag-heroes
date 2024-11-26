from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import Annotation
from schemas.annotations import AnnotationSchemaFull, AnnotationSchemaCreate
from schemas.vote import VoteSchemaFull, VoteSchemaCreate
from settings.settings import AnnotationSettings
annotations_router_settings = AnnotationSettings()

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
        user = verify_token(token)  # Ensure user is authenticated

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
        user = verify_token(token)  # Ensure user is authenticated

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
    response_model=AnnotationSchemaFull,
    description="Create a new annotation"
)
async def create_annotation(
    annotation_data: AnnotationSchemaCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> AnnotationSchemaFull:
    """
    Create a new annotation.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        # Create the new annotation
        new_annotation = Annotation(
            user_id=annotation_data.user_id,
            sdg_user_label_id=annotation_data.sdg_user_label_id,
            labeler_score=annotation_data.labeler_score,
            comment=annotation_data.comment,
        )

        db.add(new_annotation)
        db.commit()
        db.refresh(new_annotation)

        return AnnotationSchemaFull.model_validate(new_annotation)

    except Exception as e:
        logging.error(f"Error creating annotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the annotation",
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
        user = verify_token(token)  # Ensure user is authenticated

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
        user = verify_token(token)  # Ensure user is authenticated

        annotations = db.query(Annotation).all()
        return [AnnotationSchemaFull.model_validate(annotation) for annotation in annotations]

    except Exception as e:
        logging.error(f"Error fetching annotations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching annotations",
        )




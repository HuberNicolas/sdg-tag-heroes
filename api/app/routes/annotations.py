from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models import Annotation
from request_models.annotations_gpt import AnnotationEvaluationRequest, AnnotationCreateRequest
from schemas import VoteSchemaFull
from schemas.annotation import AnnotationSchemaFull
from schemas.gpt_assistant_service import AnnotationEvaluationSchema
from services.gpt.gpt_assistant_service import GPTAssistantService
from services.gpt.user_annotation_evaluator_service import UserAnnotationEvaluatorService
from settings.settings import AnnotationsSettings
from utils.logger import logger

# Setup Logging
annotations_router_settings = AnnotationsSettings()
logging = logger(annotations_router_settings.ANNOTATIONS_ROUTER_LOG_NAME)

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
    prefix="/annotations",
    tags=["Annotations"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.post(
    "/",
    response_model=AnnotationSchemaFull,
    description="Create a new annotation."
)
async def create_annotation(
        request: AnnotationCreateRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
) -> AnnotationSchemaFull:
    """
    Create a new annotation.
    """
    try:
        user = verify_token(token, db)  # Authenticate user

        # Ensure either `sdg_user_label_id` or `decision_id` is set, but not both
        if request.sdg_user_label_id and request.decision_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only one of `sdg_user_label_id` or `decision_id` should be provided.",
            )

        # Create new annotation instance
        new_annotation = Annotation(
            user_id=request.user_id,
            comment=request.comment,
            sdg_user_label_id=request.sdg_user_label_id,
            decision_id=request.decision_id,
            labeler_score=request.labeler_score,
        )

        # Add to the database
        db.add(new_annotation)
        db.commit()
        db.refresh(new_annotation)

        return AnnotationSchemaFull.model_validate(new_annotation)

    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data.",
        )
    except Exception as e:
        logging.error(f"Error creating annotation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the annotation.",
        )


@router.post(
    "/score",
    response_model=AnnotationEvaluationSchema,
    description="Evaluate an annotation against an SDG label."
)
async def evaluate_annotation_score(
        request: AnnotationEvaluationRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
) -> AnnotationEvaluationSchema:
    """
    Evaluate an annotation's scores for relevance, depth, correctness, and creativity.
    """
    try:
        user = verify_token(token, db)  # Authenticate user

        # Init here since might be heavy
        gpt_service = GPTAssistantService()
        evaluator_service = UserAnnotationEvaluatorService()

        # Get LLM scores from GPT
        llm_scores = gpt_service.evaluate_annotation(
            passage=request.passage,
            annotation=request.annotation,
            sdg_label=request.sdg_label,
        )

        # Get semantic similarity and combined score
        evaluation_result = evaluator_service.evaluate_annotation(
            passage=request.passage,
            annotation=request.annotation,
            sdg_label=request.sdg_label,
            llm_scores=llm_scores,
        )

        # Return the evaluation result
        return AnnotationEvaluationSchema.model_validate(evaluation_result)

    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input. Please check your request data.",
        )
    except Exception as e:
        logging.error(f"Error evaluating annotation score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating the annotation score.",
        )


@router.get(
    "/label-decisions/{label_decision_id}",
    response_model=List[AnnotationSchemaFull],
    description="Retrieve all annotations for a specific label decision."
)
async def get_annotations_by_label_decision(
        label_decision_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
) -> List[AnnotationSchemaFull]:
    """
    Retrieve all annotations associated with a specific SDG label decision.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        annotations = db.query(Annotation).filter(Annotation.decision_id == label_decision_id).all()

        if not annotations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No annotations found for label decision ID {label_decision_id}.",
            )

        return [AnnotationSchemaFull.model_validate(annotation) for annotation in annotations]

    except Exception as e:
        logging.error(f"Error fetching annotations for label decision ID {label_decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching annotations for the label decision.",
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

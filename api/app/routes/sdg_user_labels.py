from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from enums import SDGType
from models import SDGUserLabel, SDGLabelDecision, sdg_label_decision_user_label_association, Vote, Annotation
from models.publications.publication import Publication
from models.sdg_label_summary import SDGLabelSummary
from request_models.annotations_gpt import AnnotationEvaluationRequest
from request_models.sdg_user_label import UserLabelRequest, UserLabelIdsRequest
from schemas import SDGUserLabelSchemaFull, SDGUserLabelSchemaBase
from schemas.gpt_assistant_service import GPTResponseCommentSummarySchema, SDGUserLabelsCommentSummarySchema, \
    AnnotationEvaluationSchema
from schemas.sdg_label_decision import SDGLabelDecisionSchemaExtended
from schemas.sdg_user_label import SDGUserLabelStatisticsSchema, SDGLabelDistribution, UserVotingDetails
from schemas.vote import VoteSchemaFull
from services.gpt.gpt_assistant_service import GPTAssistantService
from services.gpt.user_annotation_evaluator_service import UserAnnotationEvaluatorService
from services.label_service import LabelService
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

# Use the GPT Assistant service for user-label-centred operations
assistant = GPTAssistantService()

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

@router.post(
    "/{user_label_id}/evaluate",
    response_model=AnnotationEvaluationSchema,
    description="Evaluate a user label's comment against the abstract selection."
)
async def evaluate_user_label(
    user_label_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> AnnotationEvaluationSchema:
    """
    Evaluate a user label's comment in relation to the abstract selection.
    Returns zero scores if the label lacks an abstract section or a comment.
    """
    try:
        user = verify_token(token, db)  # Authenticate user

        # Fetch the user label
        user_label = db.query(SDGUserLabel).filter(SDGUserLabel.label_id == user_label_id).first()

        if not user_label:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDG user label with ID {user_label_id} not found",
            )

        # Handle missing abstract section or comment by returning zero scores
        if not user_label.abstract_section or not user_label.comment:
            return AnnotationEvaluationSchema(
                passage=user_label.abstract_section or "",
                annotation=user_label.comment or "",
                sdg_label=SDGType(f"sdg{user_label.voted_label}") if user_label.voted_label else SDGType("sdg0"),
                relevance=0.0,
                depth=0.0,
                correctness=0.0,
                creativity=0.0,
                reasoning="Insufficient data for evaluation.",
                llm_score=0.0,
                semantic_score=0.0,
                combined_score=0.0,
            )

        # Initialize services
        gpt_service = GPTAssistantService()
        evaluator_service = UserAnnotationEvaluatorService()

        # Get LLM evaluation scores
        llm_scores = gpt_service.evaluate_annotation(
            passage=user_label.abstract_section,
            annotation=user_label.comment,
            sdg_label=SDGType(f"sdg{user_label.voted_label}"),
        )

        # Compute semantic similarity and final score
        evaluation_result = evaluator_service.evaluate_annotation(
            passage=user_label.abstract_section,
            annotation=user_label.comment,
            sdg_label=SDGType(f"sdg{user_label.voted_label}"),
            llm_scores=llm_scores,
        )

        return AnnotationEvaluationSchema.model_validate(evaluation_result)

    except ValidationError as ve:
        logging.error(f"Validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data.",
        )
    except Exception as e:
        logging.error(f"Error evaluating user label {user_label_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating the user label.",
        )



@router.post(
    "/summary", # TODO: Rename into comments/summary
    response_model=SDGUserLabelsCommentSummarySchema,
    description="Summarize a collection of SDG user comments into a cohesive summary."
)
async def create_comment_summary(
    request: UserLabelIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> SDGUserLabelsCommentSummarySchema:
    """
    Given a list of SDG user label IDs, retrieve their comments and generate a summary.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        user_labels_ids = request.user_labels_ids

        # Fetch the user labels based on the provided label IDs
        user_labels = db.query(SDGUserLabel).filter(SDGUserLabel.label_id.in_(user_labels_ids)).all()

        if not user_labels:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No SDG user labels found for the given IDs."
            )

        # Prepare data for summarization (just the comment field)
        user_labels_data = [
            {"comment": label.comment or "No comment provided"} for label in user_labels
        ]

        # Call the assistant to generate the summary and keywords
        summary_response = assistant.summarize_comments(user_labels=user_labels_data)

        return SDGUserLabelsCommentSummarySchema(
            user_labels_ids = user_labels_ids,
            summary=summary_response.summary,
        )

    except HTTPException as he:
        raise he  # Re-raise HTTPException to return specific error responses
    except Exception as e:
        logging.error(f"Error creating summary for user labels: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the comment summary.",
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
    "/label-decisions/{decision_id}/",
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
    "/label-decisions/{decision_id}/{label_id}",
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

@router.post(
    "/",
    response_model=SDGUserLabelSchemaFull,
    description="Create or link an SDG user label"
)
async def create_sdg_user_label(
    request: UserLabelRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGUserLabelSchemaFull:
    """
    Create or link an SDG user label.
    """
    try:

        user = verify_token(token, db)  # Ensure user is authenticated
        label_service = LabelService(db)
        print(request)

        new_user_label = label_service.create_or_link_label(request)
        return SDGUserLabelSchemaFull.model_validate(new_user_label)

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error creating or linking SDG user label: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating or linking the SDG user label",
        )

@router.get(
    "/label-decisions/{decision_id}/statistics/",
    response_model=SDGUserLabelStatisticsSchema,
    description="Retrieve statistics for SDGUserLabels, including label distribution, user voting details, and full entities.",
)
async def get_sdg_user_labels_statistics(
    decision_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGUserLabelStatisticsSchema:
    """
    Retrieve statistics for SDGUserLabels, including label distribution, user voting details, and full entities.
    Only the last SDGUserLabel per decision per user is considered for the filtered distribution.
    All votes are included in the user voting details.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Initialize the service
        label_service = LabelService(db)

        # Get the statistics
        return label_service.get_statistics(decision_id)

    except HTTPException as he:
        raise he  # Re-raise HTTPException to return specific error responses
    except Exception as e:
        logging.error(f"Error fetching SDGUserLabel statistics with entities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDGUserLabel statistics with entities",
        )

@router.get(
    "/users/{user_id}",
    response_model=List[SDGLabelDecisionSchemaExtended],
    description="Retrieve all SDG label decisions a user has interacted with, along with their associated labels and annotations."
)
async def get_user_interacted_sdg_label_decisions(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaExtended]:
    """
    Retrieve all SDGLabelDecisions that a user has interacted with, including:
    - All associated SDGUserLabels
    - All annotations linked to those labels
    - All annotations directly linked to the decision
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Fetch all SDGLabelDecisions where the user has created an SDGUserLabel
        user_label_decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelDecision.user_labels)
            .filter(SDGUserLabel.user_id == user_id)
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Fetch all SDGLabelDecisions where the user has created an annotation directly linked to the decision
        annotation_decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelDecision.annotations)
            .filter(Annotation.user_id == user_id)
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Fetch all SDGLabelDecisions where the user has created an annotation linked to an SDGUserLabel associated with a decision
        annotation_user_label_decisions = (
            db.query(SDGLabelDecision)
            .join(SDGLabelDecision.user_labels)
            .join(SDGUserLabel.annotations)
            .filter(Annotation.user_id == user_id)
            .options(
                joinedload(SDGLabelDecision.user_labels).joinedload(SDGUserLabel.annotations),
                joinedload(SDGLabelDecision.annotations)
            )
            .all()
        )

        # Combine results and remove duplicates
        all_decisions = list(set(user_label_decisions + annotation_decisions + annotation_user_label_decisions))

        if not all_decisions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelDecisions found for user ID {user_id}",
            )

        return [SDGLabelDecisionSchemaExtended.model_validate(decision) for decision in all_decisions]

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching SDGLabelDecisions for user {user_id}.",
        )


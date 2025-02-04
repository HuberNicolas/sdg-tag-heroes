from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models import SDGUserLabel, SDGLabelDecision, sdg_label_decision_user_label_association, Vote
from models.publications.publication import Publication
from models.sdg_label_summary import SDGLabelSummary
from request_models.sdg_user_label import UserLabelRequest, UserLabelIdsRequest
from schemas import SDGUserLabelSchemaFull, SDGUserLabelSchemaBase
from schemas.gpt_assistant_service import GPTResponseCommentSummarySchema, SDGUserLabelsCommentSummarySchema
from schemas.sdg_user_label import SDGUserLabelStatisticsSchema, SDGLabelDistribution, UserVotingDetails
from schemas.vote import VoteSchemaFull
from services.gpt.gpt_assistant_service import GPTAssistantService
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
    "/summary",
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

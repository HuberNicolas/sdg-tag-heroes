from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models.publications.publication import Publication
from schemas import SDGLabelDecisionSchemaFull
from settings.settings import SDGSLabelDecisionsRouterSettings
from utils.logger import logger

# Setup Logging
sdg_label_decisions_router_settings = SDGSLabelDecisionsRouterSettings()
logging = logger(sdg_label_decisions_router_settings.SDGLABELDECISIONS_ROUTER_LOG_NAME)

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

# Create the API Router
router = APIRouter(
    prefix="/label-decisions",
    tags=["Label Decisions"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get(
    "/publications/{publication_id}",
    response_model=List[SDGLabelDecisionSchemaFull],
    description="Retrieve all SDGLabelDecision entries associated with a publication's SDGLabelHistory"
)
async def get_sdg_label_decisions(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaFull]:
    """
    Retrieve all SDGLabelDecision entries for a publication's SDGLabelHistory.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelHistory
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        history = publication.sdg_label_summary.history

        if not history or not history.decisions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelDecision entries found for publication ID {publication_id}",
            )

        return [SDGLabelDecisionSchemaFull.model_validate(decision) for decision in history.decisions]

    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecisions for the publication",
        )


@router.get(
    "/publications/{publication_id}/{decision_id}",
    response_model=SDGLabelDecisionSchemaFull,
    description="Retrieve a specific SDGLabelDecision entry associated with a publication's SDGLabelHistory"
)
async def get_sdg_label_decision(
    publication_id: int,
    decision_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelDecisionSchemaFull:
    """
    Retrieve a specific SDGLabelDecision entry for a publication's SDGLabelHistory.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelHistory
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        history = publication.sdg_label_summary.history

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found for publication ID {publication_id}",
            )

        decision = next((d for d in history.decisions if d.decision_id == decision_id), None)

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found for publication ID {publication_id}",
            )

        return SDGLabelDecisionSchemaFull.model_validate(decision)

    except Exception as e:
        logging.error(
            f"Error fetching SDGLabelDecision ID {decision_id} for publication ID {publication_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecision for the publication",
        )

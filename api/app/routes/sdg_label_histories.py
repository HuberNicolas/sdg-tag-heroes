from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from sqlalchemy.orm import Session, sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrant_client
from models import SDGLabelHistory
from models.publications.publication import Publication
from requests_models.publication import PublicationIdsRequest
from requests_models.publication_similarity_query_service import PublicationSimilarityQueryRequest
from schemas import PublicationSchemaBase, PublicationSchemaFull, SDGLabelDecisionSchemaFull, SDGLabelHistorySchemaFull
from api.app.routes.authentication import verify_token
from api.app.security import Security
from schemas.services.publication_similarity_query_service import PublicationSimilaritySchema
from services.publication_similarity_query_service import PublicationSimilarityQueryService
from settings.settings import SDGSLabelHistoriesRouterSettings
from utils.logger import logger

# Setup Logging
sdg_label_histories_router_settings = SDGSLabelHistoriesRouterSettings()
logging = logger(sdg_label_histories_router_settings.SDGLABELHISTORIES_ROUTER_LOG_NAME)

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
    prefix="/label-histories",
    tags=["Label Histories"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)


@router.get(
    "/publications/{publication_id}/",
    response_model=SDGLabelHistorySchemaFull,
    description="Retrieve the SDGLabelHistory associated with a specific publication"
)
async def get_sdg_label_history(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelHistorySchemaFull:
    """
    Retrieve the SDGLabelHistory for a specific publication.
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

        return SDGLabelHistorySchemaFull.model_validate(history)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelHistory for the publication",
        )

@router.get(
    "/{history_id}/",
    response_model=SDGLabelHistorySchemaFull,
    description="Retrieve the a specific SDGLabelHistory"
)
async def get_sdg_label_history(
    history_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelHistorySchemaFull:
    """
    Retrieve the SDGLabelHistory for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the SDGLabelHistory
        history = db.query(SDGLabelHistory).filter(SDGLabelHistory.history_id == history_id).first()

        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelHistory found with ID {history_id}",
            )

        return SDGLabelHistorySchemaFull.model_validate(history)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the SDGLabelHistory with ID {history_id}: {str(e)}",
        )

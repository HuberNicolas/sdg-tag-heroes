import time
from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import PublicationQuery, SimilarityQueryRequest
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrant_client

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import SDGPrediction, SDGLabelDecision, Fact, Summary
from models.publications.author import Author
# Import models
from models.publications.publication import Publication
from models.request import PublicationIdsRequest

from schemas.dimensionality_reduction import DimensionalityReductionSchemaBase, DimensionalityReductionSchemaFull
from schemas.publications.author import AuthorSchemaBase, AuthorSchemaFull
from schemas.publications.publication import PublicationSchemaBase, PublicationSchemaFull
from schemas.sdg_label_decision import SDGLabelDecisionSchemaBase, SDGLabelDecisionSchemaFull
from schemas.sdg_label_history import SDGLabelHistorySchemaFull
from schemas.sdg_label_summary import SDGLabelSummarySchemaFull
from schemas.sdg_prediction import SDGPredictionSchemaFull, SDGPredictionSchemaBase
from schemas.sdg_user_label import SDGUserLabelSchemaFull, SDGUserLabelSchemaBase

from services.gpt_explainer import SDGExplainer, SummarizePublicationStrategy, CollectiveSummaryResponse
from services.similarity_query import SimilarityQuery

from settings.settings import PublicationsRouterSettings
publications_router_settings = PublicationsRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(publications_router_settings.PUBLICATIONS_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/publications",
    tags=["publications"],
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
    "/sdg_label_decisions/{decision_id}/sdg_user_labels",
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

        # Query the database for the SDGLabelDecision
        decision = db.query(SDGLabelDecision).filter(SDGLabelDecision.decision_id == decision_id).first()

        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SDGLabelDecision with ID {decision_id} not found",
            )

        # Return the list of SDGUserLabels associated with the decision
        return [SDGUserLabelSchemaBase.model_validate(label) for label in decision.user_labels]

    except Exception as e:
        logging.error(f"Error fetching SDGUserLabels for decision ID {decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDGUserLabels for the decision",
        )

@router.get(
    "/sdg_label_decisions/{decision_id}/sdg_user_labels/{label_id}",
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

        # Query the database for the SDGLabelDecision
        decision = db.query(SDGLabelDecision).filter(SDGLabelDecision.decision_id == decision_id).first()

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

    except Exception as e:
        logging.error(f"Error fetching SDGUserLabel ID {label_id} for decision ID {decision_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGUserLabel for the decision",
        )


@router.get(
    "/{publication_id}/sdg_label_history",
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
        logging.error(f"Error fetching SDGLabelHistory for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelHistory for the publication",
        )

@router.get(
    "/{publication_id}/sdg_label_summary",
    response_model=SDGLabelSummarySchemaFull,
    description="Retrieve the SDGLabelSummary associated with a specific publication"
)
async def get_sdg_label_summary(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> SDGLabelSummarySchemaFull:
    """
    Retrieve the SDGLabelSummary for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its SDGLabelSummary
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication or not publication.sdg_label_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No SDGLabelSummary found for publication ID {publication_id}",
            )

        return SDGLabelSummarySchemaFull.model_validate(publication.sdg_label_summary)

    except Exception as e:
        logging.error(f"Error fetching SDGLabelSummary for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelSummary for the publication",
        )

@router.get(
    "/{publication_id}/sdg_label_history/decisions",
    response_model=List[SDGLabelDecisionSchemaBase],
    description="Retrieve all SDGLabelDecision entries associated with a publication's SDGLabelHistory"
)
async def get_sdg_label_decisions(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGLabelDecisionSchemaBase]:
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

        return [SDGLabelDecisionSchemaBase.model_validate(decision) for decision in history.decisions]

    except Exception as e:
        logging.error(f"Error fetching SDGLabelDecisions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDGLabelDecisions for the publication",
        )


@router.get(
    "/{publication_id}/sdg_label_history/decisions/{decision_id}",
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

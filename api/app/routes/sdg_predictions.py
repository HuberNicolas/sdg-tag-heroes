from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import PublicationQuery
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import SDGPrediction
from models.publications.publication import Publication
from models.request import SDGPredictionsIdsRequest, SDGPredictionsPublicationsIdsRequest
from schemas import SDGPredictionSchemaFull
from settings.settings import SDGPredictionsRouterSettings
sdg_predictions_router_settings = SDGPredictionsRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(sdg_predictions_router_settings.SDGPREDICTIONS_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/sdg_predictions",
    tags=["SDG Predictions"],
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
    "/publications",
    response_model=List[SDGPredictionSchemaFull],
    description="Get predictions for a list of publication IDs"
)
async def get_predictions_by_publication_ids(
        request: SDGPredictionsPublicationsIdsRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    """
    Fetch predictions based on publication IDs.

    Args:
        request (List[int]): List of publication IDs.
        db (Session): Database session.
        token (str): Authentication token.

    Returns:
        List[SDGPredictionSchemaFull]: List of predictions for the provided publication IDs.
    """
    # Authenticate the user
    user = verify_token(token)

    # Extract the publication IDs from the request
    publications_ids = request.publications_ids  # Access the list of IDs

    # Fetch the predictions by joining publications and sdg_predictions
    predictions = (
        db.query(SDGPrediction)
        .join(Publication, SDGPrediction.publication_id == Publication.publication_id)
        .filter(Publication.publication_id.in_(publications_ids))
        .filter(SDGPrediction.prediction_model == "Aurora")
        .all()
    )

    # Return the predictions as the specified schema
    return [SDGPredictionSchemaFull.model_validate(prediction) for prediction in predictions]



@router.post(
    "/",
    response_model=List[SDGPredictionSchemaFull],
    description="Get a list of predictions by IDs"
)
async def get_publications_by_ids(
    request: SDGPredictionsIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    user = verify_token(token)  # Ensure user is authenticated
    sdg_predictions_ids = request.sdg_predictions_ids  # Access the list of IDs
    publications = db.query(SDGPrediction).filter(SDGPrediction.prediction_id.in_(sdg_predictions_ids)).all()
    return [SDGPredictionSchemaFull.model_validate(pub) for pub in publications]


@router.get(
    "/publications/{publication_id}",
    response_model=List[SDGPredictionSchemaFull],
    description="Get predictions for a single publication ID"
)
async def get_publications_by_ids(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    user = verify_token(token)  # Ensure user is authenticated
    publication= db.query(SDGPrediction).filter(SDGPrediction.prediction_id == publication_id).filter(SDGPrediction.prediction_model == "Aurora").first()
    return [SDGPredictionSchemaFull.model_validate(publication)]

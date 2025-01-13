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
from services.al_service import ALCalculationService
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
    user = verify_token(token, db)

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
    user = verify_token(token, db)  # Ensure user is authenticated
    sdg_predictions_ids = request.sdg_predictions_ids  # Access the list of IDs
    publications = db.query(SDGPrediction).filter(SDGPrediction.prediction_id.in_(sdg_predictions_ids)).all()
    return [SDGPredictionSchemaFull.model_validate(pub) for pub in publications]


@router.get(
    "/publications/{publication_id}",
    response_model=List[SDGPredictionSchemaFull],
    description="Get predictions for a single publication ID"
)
async def get_publication_by_id(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Perform a JOIN between Publication and SDGPrediction
    publication = db.query(Publication).join(
        SDGPrediction, SDGPrediction.publication_id == Publication.publication_id
    ).filter(
        Publication.publication_id == publication_id,
        SDGPrediction.prediction_model == "Aurora"
    ).first()

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail=f"Publication with ID {publication_id} not found or no Aurora model prediction available."
        )

    # Return the SDG predictions for the matched publication
    # Since the query fetches the entire Publication and its SDG predictions, we can now return them
    return [SDGPredictionSchemaFull.model_validate(prediction) for prediction in publication.sdg_predictions]


@router.post(
    "/publications/metrics",
    response_model=List[Dict[str, Any]],
    description="Get distribution metrics (entropy and standard deviation) for a list of publication IDs"
)
async def get_distribution_metrics_by_publication_ids(
    request: SDGPredictionsPublicationsIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[Dict[str, Any]]:
    """
    Calculate distribution metrics (entropy and standard deviation) for a list of publication IDs.

    Args:
        request (SDGPredictionsPublicationsIdsRequest): Request containing a list of publication IDs.
        db (Session): Database session.
        token (str): Authentication token.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing publication ID, entropy, and standard deviation.
    """
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Extract publication IDs from the request
    publication_ids = request.publications_ids

    # Query SDG predictions for the given publication IDs
    sdg_predictions = (
        db.query(SDGPrediction)
        .filter(SDGPrediction.publication_id.in_(publication_ids))
        .all()
    )

    if not sdg_predictions:
        raise HTTPException(
            status_code=404,
            detail=f"No SDG predictions found for the provided publication IDs."
        )

    # Initialize the service
    service = ALCalculationService()

    # Calculate metrics for each prediction
    results = []
    for prediction in sdg_predictions:
        sdg_values = [
            prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4,
            prediction.sdg5, prediction.sdg6, prediction.sdg7, prediction.sdg8,
            prediction.sdg9, prediction.sdg10, prediction.sdg11, prediction.sdg12,
            prediction.sdg13, prediction.sdg14, prediction.sdg15, prediction.sdg16,
            prediction.sdg17
        ]
        entropy = service.calculate_entropy(sdg_values)
        sd = service.calculate_standard_deviation(sdg_values)

        results.append({
            "publication_id": prediction.publication_id,
            "entropy": entropy,
            "standard_deviation": sd,
        })

    return results



@router.get(
    "/publications/{publication_id}/metrics",
    response_model=Dict[str, Any],
    description="Get entropy and standard deviation for the predictions of a single publication ID"
)
async def get_publication_metrics_by_id(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    Fetch the entropy and standard deviation for the SDG prediction values of a specific publication.

    Args:
        publication_id (int): The ID of the publication.
        db (Session): Database session.
        token (str): Authentication token.

    Returns:
        Dict[str, Any]: A dictionary with entropy and standard deviation of the predictions.
    """
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Fetch the SDG predictions for the publication
    sdg_prediction = (
        db.query(SDGPrediction)
        .filter(SDGPrediction.publication_id == publication_id)
        .first()
    )

    if not sdg_prediction:
        raise HTTPException(
            status_code=404,
            detail=f"SDG predictions for publication ID {publication_id} not found."
        )

    # Calculate entropy and standard deviation
    sdg_values = [
        sdg_prediction.sdg1, sdg_prediction.sdg2, sdg_prediction.sdg3, sdg_prediction.sdg4,
        sdg_prediction.sdg5, sdg_prediction.sdg6, sdg_prediction.sdg7, sdg_prediction.sdg8,
        sdg_prediction.sdg9, sdg_prediction.sdg10, sdg_prediction.sdg11, sdg_prediction.sdg12,
        sdg_prediction.sdg13, sdg_prediction.sdg14, sdg_prediction.sdg15, sdg_prediction.sdg16,
        sdg_prediction.sdg17
    ]

    service = ALCalculationService()
    entropy = service.calculate_entropy(sdg_values)
    sd = service.calculate_standard_deviation(sdg_values)

    return {
        "publication_id": publication_id,
        "entropy": entropy,
        "standard_deviation": sd,
    }

@router.get(
    "/publications/metrics/{metric_type}/{order}/{top_n}",
    response_model=List[Dict[str, Any]],
    description="Get top or bottom N publications based on entropy or standard deviation"
)
async def get_publications_by_metric(
    metric_type: str,
    order: str,
    top_n: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[Dict[str, Any]]:
    """
    Fetch the top or bottom N publications based on entropy or standard deviation.

    Args:
        metric_type (str): The metric type to rank by ("entropy" or "standard_deviation").
        order (str): Specify "top" for highest or "bottom" for lowest.
        top_n (int): Number of results to return.
        db (Session): Database session.
        token (str): Authentication token.

    Returns:
        List[Dict[str, Any]]: List of dictionaries with publication ID, metric value, and metric type.
    """
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Validate metric type
    if metric_type not in {"entropy", "standard_deviation"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid metric type. Allowed values are 'entropy' or 'standard_deviation'."
        )

    # Validate order
    if order not in {"top", "bottom"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid order value. Allowed values are 'top' or 'bottom'."
        )

    # Validate top_n
    if top_n <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid top_n value. It must be a positive integer."
        )

    # Query all SDG predictions
    sdg_predictions = db.query(SDGPrediction).all()

    if not sdg_predictions:
        raise HTTPException(
            status_code=404,
            detail="No SDG predictions found."
        )

    # Initialize the service
    service = ALCalculationService()

    # Calculate metrics for each prediction
    metrics = []
    for prediction in sdg_predictions:
        sdg_values = [
            prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4,
            prediction.sdg5, prediction.sdg6, prediction.sdg7, prediction.sdg8,
            prediction.sdg9, prediction.sdg10, prediction.sdg11, prediction.sdg12,
            prediction.sdg13, prediction.sdg14, prediction.sdg15, prediction.sdg16,
            prediction.sdg17
        ]
        entropy = service.calculate_entropy(sdg_values)
        sd = service.calculate_standard_deviation(sdg_values)

        metrics.append({
            "publication_id": prediction.publication_id,
            "entropy": entropy,
            "standard_deviation": sd,
        })

    # Sort by the specified metric in the correct order
    reverse_order = order == "top"
    sorted_results = sorted(
        metrics, key=lambda x: x[metric_type], reverse=reverse_order
    )[:top_n]

    # Add metric type to the response for clarity
    for entry in sorted_results:
        entry["metric_type"] = metric_type
        entry["order"] = order

    return sorted_results

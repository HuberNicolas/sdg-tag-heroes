from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union, Literal

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import PublicationQuery, SDGFilterQuery
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import SDGPrediction
from models.publications.publication import Publication
from requests_models.sdg_prediction import SDGPredictionsPublicationsIdsRequest, SDGPredictionsIdsRequest
from schemas import SDGPredictionSchemaFull
from services.al_service import ALCalculationService
from settings.settings import SDGPredictionsRouterSettings
from utils.logger import logger

# Setup Logging
sdg_predictions_router_settings = SDGPredictionsRouterSettings()
logging = logger(sdg_predictions_router_settings.SDGPREDICTIONS_ROUTER_LOG_NAME)
logging.info(f"Default model: {sdg_predictions_router_settings.DEFAULT_MODEL}")

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
    prefix="/sdg-predictions",
    tags=["SDG Predictions"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.post(
    "/",
    response_model=List[SDGPredictionSchemaFull],
    description="Get a list of predictions by IDs"
)
async def get_sdg_predictions_by_ids(
    request: SDGPredictionsIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        sdg_predictions_ids = request.sdg_predictions_ids  # Access the list of IDs

        # Fetch predictions by IDs
        publications = db.query(SDGPrediction).filter(SDGPrediction.prediction_id.in_(sdg_predictions_ids)).all()

        # Return the predictions as the specified schema
        return [SDGPredictionSchemaFull.model_validate(pub) for pub in publications]

    except HTTPException as he:
        # Re-raise HTTPException to return specific error responses
        raise he
    except Exception as e:
        logging.error(f"Error fetching SDG predictions by IDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG predictions by IDs.",
        )

@router.post(
    "/publications",
    response_model=List[SDGPredictionSchemaFull],
    description="Get SDG predictions for a list of publication IDs"
)
async def get_sdg_predictions_by_publication_ids(
    request: SDGPredictionsPublicationsIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Extract the publication IDs from the request
        publications_ids = request.publications_ids  # Access the list of IDs

        # Fetch the predictions by joining publications and sdg_predictions
        predictions = (
            db.query(SDGPrediction)
            .join(Publication, SDGPrediction.publication_id == Publication.publication_id)
            .filter(Publication.publication_id.in_(publications_ids))
            .filter(SDGPrediction.prediction_model == sdg_predictions_router_settings.DEFAULT_MODEL)
            .all()
        )

        # Return the predictions as the specified schema
        return [SDGPredictionSchemaFull.model_validate(prediction) for prediction in predictions]

    except HTTPException as he:
        # Re-raise HTTPException to return specific error responses
        raise he
    except Exception as e:
        logging.error(f"Error fetching SDG predictions by publication IDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG predictions by publication IDs.",
        )

@router.get(
    "/publications/{publication_id}",
    response_model=List[SDGPredictionSchemaFull],
    description="Get all SDG predictions for a single publication ID"
)
async def get_sdg_predictions_by_publication_id(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Fetch the publication and its SDG predictions filtered by prediction_model
        publication = db.query(Publication).join(
            SDGPrediction, SDGPrediction.publication_id == Publication.publication_id
        ).filter(
            Publication.publication_id == publication_id,
        ).first()

        if publication is None:
            raise HTTPException(
                status_code=404,
                detail=f"Publication with ID {publication_id} not found or no model predictions available."
            )

        # Return the SDG predictions for the matched publication
        # Query fetches the entire Publication and its SDG predictions, we can now return them
        return [SDGPredictionSchemaFull.model_validate(prediction) for prediction in publication.sdg_predictions]

    except HTTPException as he:
        # Re-raise HTTPException to return specific error responses
        raise he
    except Exception as e:
        logging.error(f"Error fetching SDG predictions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG predictions for the publication.",
        )

@router.get(
    "/publications/default-model/{publication_id}",
    response_model=List[SDGPredictionSchemaFull],
    description="Get all default model SDG predictions for a single publication ID"
)
async def get_default_model_sdg_predictions_by_publication_id(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[SDGPredictionSchemaFull]:
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Fetch the publication
        publication = db.query(Publication).filter(
            Publication.publication_id == publication_id
        ).first()

        if publication is None:
            raise HTTPException(
                status_code=404,
                detail=f"Publication with ID {publication_id} not found."
            )

        # Filter the SDG predictions by prediction_model (Aurora)
        default_model_predictions = [
            prediction for prediction in publication.sdg_predictions
            if prediction.prediction_model == sdg_predictions_router_settings.DEFAULT_MODEL
        ]

        if not default_model_predictions:
            raise HTTPException(
                status_code=404,
                detail=f"No {sdg_predictions_router_settings.DEFAULT_MODEL} model predictions available for publication ID {publication_id}."
            )

        # Return the filtered SDG predictions
        return [SDGPredictionSchemaFull.model_validate(prediction) for prediction in default_model_predictions]

    except HTTPException as he:
        # Re-raise HTTPException to return specific error responses
        raise he
    except Exception as e:
        logging.error(f"Error fetching SDG predictions for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG predictions for the publication.",
        )

if False:

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
    from fastapi import HTTPException, Request


    @router.post(
        "/publications/metrics/filter/{metric_type}/{order}/{top_n}",
        response_model=Dict[str, Any],
        description=(
            "Filter publications by SDG values and rank by entropy or standard deviation. "
            "Supports optional filtering by SDG field and no_high_predictions."
        )
    )
    async def post_filter_publications_by_metric(
        metric_type: Literal["entropy", "standard_deviation"],
        order: Literal["top", "bottom"],
        top_n: int,
        request: Request,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> Dict[str, Any]:
        # Ensure user is authenticated
        user = verify_token(token, db)

        # Parse the JSON body
        body = await request.json()
        print(f"Received body: {body}")

        # Validate required fields in the body
        if "sdg_field" not in body or body["sdg_field"] is None:
            raise HTTPException(
                status_code=400,
                detail="Missing or invalid 'sdg_field'."
            )
        if "lower_limit" not in body or "upper_limit" not in body:
            raise HTTPException(
                status_code=400,
                detail="Missing 'lower_limit' or 'upper_limit'."
            )

        # Initialize SDGFilterQuery
        # TODO: make more robust, this is a bit sketchy, but accessing the sdg directly somehow fails
        sdg_query = SDGFilterQuery(**body)

        # Define all SDG fields
        sdg_fields = [f"sdg{i}" for i in range(1, 18)]

        # Validate sdg_field
        if sdg_query.sdg_field not in sdg_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sdg_field '{sdg_query.sdg_field}'. Allowed fields: {', '.join(sdg_fields)}"
            )

        # Filter rows based on the primary sdg_field
        query = db.query(SDGPrediction).filter(
            SDGPrediction.prediction_model == "Aurora",
            getattr(SDGPrediction, sdg_query.sdg_field).between(
                sdg_query.lower_limit, sdg_query.upper_limit
            )
        )

        # Fetch initial filtered results
        filtered_predictions = query.all()

        if not filtered_predictions:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No predictions found with {sdg_query.sdg_field} values "
                    f"between {sdg_query.lower_limit} and {sdg_query.upper_limit}."
                )
            )

        # Further filter based on no_high_predictions
        final_predictions = []
        for prediction in filtered_predictions:
            # Count how many other SDG fields fall into the range
            other_sdg_count = sum(
                1 for field in sdg_fields
                if field != sdg_query.sdg_field and
                getattr(prediction, field) and
                sdg_query.lower_limit <= getattr(prediction, field) <= sdg_query.upper_limit
            )

            # Include if the count matches (or exceeds >=)  no_high_predictions
            if other_sdg_count == sdg_query.no_high_predictions:
                final_predictions.append(prediction)

        # Initialize the service
        service = ALCalculationService()

        # Calculate metrics for each prediction
        metrics = []
        for prediction in final_predictions:
            # Extract SDG values dynamically
            sdg_values = [getattr(prediction, field) for field in sdg_fields]
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

        # Calculate summary statistics
        if metrics:
            highest_entropy = max(metrics, key=lambda x: x["entropy"])
            lowest_entropy = min(metrics, key=lambda x: x["entropy"])
            highest_std_dev = max(metrics, key=lambda x: x["standard_deviation"])
            lowest_std_dev = min(metrics, key=lambda x: x["standard_deviation"])
        else:
            highest_entropy = lowest_entropy = highest_std_dev = lowest_std_dev = None

        # Add metric type and order to the response for clarity
        for entry in sorted_results:
            entry["metric_type"] = metric_type
            entry["order"] = order

        # Add summary statistics
        summary_statistics = {
            "number_of_results": len(sorted_results),
            "highest_entropy": highest_entropy["entropy"] if highest_entropy else None,
            "lowest_entropy": lowest_entropy["entropy"] if lowest_entropy else None,
            "highest_standard_deviation": highest_std_dev["standard_deviation"] if highest_std_dev else None,
            "lowest_standard_deviation": lowest_std_dev["standard_deviation"] if lowest_std_dev else None,
        }

        return {
            "summary_statistics": summary_statistics,
            "sorted_results": sorted_results,
        }

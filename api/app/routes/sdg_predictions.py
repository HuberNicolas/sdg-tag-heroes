from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, sessionmaker, aliased

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from enums.enums import LevelType, ScenarioType
from models import SDGPrediction, SDGLabelDecision
from models.publications.dimensionality_reduction import DimensionalityReduction
from models.publications.publication import Publication
from request_models.sdg_prediction import SDGPredictionsPublicationsIdsRequest, SDGPredictionsIdsRequest
from schemas import SDGPredictionSchemaFull
from services.math_service import MathService
from services.metrics_service import MetricsService
from settings.settings import SDGPredictionsRouterSettings, MariaDBSettings
from utils.logger import logger

# Setup Logging
sdg_predictions_router_settings = SDGPredictionsRouterSettings()
mariadb_settings = MariaDBSettings()
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

# Use the Metrics service to calculate AL
math_service = MathService()
metrics_service = MetricsService(math_service=math_service)


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
    "/publications/{publication_id}/default-model",
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

        # Filter the SDG predictions by prediction_model
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


@router.get(
    "/dimensionality-reductions/sdgs/{sdg}/{reduction_shorthand}/{level}/",
    response_model=List[SDGPredictionSchemaFull],
    description="Retrieve SDG predictions for a given SDG, reduction shorthand, and level."
)
async def get_sdg_predictions_for_dimensionality_reductions(
    sdg: int,
    reduction_shorthand: str,
    level: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGPredictionSchemaFull]:
    try:
        user = verify_token(token, db)

        level_type = {1: LevelType.LEVEL_1, 2: LevelType.LEVEL_2, 3: LevelType.LEVEL_3}.get(level)
        if not level_type:
            raise HTTPException(status_code=400, detail="Invalid level. Must be 1, 2, or 3.")

        min_value, max_value = level_type.min_value, level_type.max_value

        sdg_predictions = (
            db.query(SDGPrediction)
            .join(DimensionalityReduction, SDGPrediction.publication_id == DimensionalityReduction.publication_id)
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                getattr(SDGPrediction, f"sdg{sdg}").between(min_value, max_value),
                SDGPrediction.prediction_model == "Aurora"
            )
            .order_by(SDGPrediction.publication_id)
            #.limit(mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE)
            .all()
        )

        logging.info(f"Retrieved {len(sdg_predictions)} SDG predictions for SDG {sdg}, level {level}, and reduction shorthand '{reduction_shorthand}'.")
        logging.info(f"Returning {len(sdg_predictions[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE])} SDG predictions for SDG {sdg}, level {level}, and reduction shorthand '{reduction_shorthand}'.")

        return sdg_predictions[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDG predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching SDG predictions: {e}")

@router.get(
    "/dimensionality-reductions/sdgs/{sdg}/{reduction_shorthand}/scenarios/{scenario_type}/",
    response_model=List[SDGPredictionSchemaFull],
    description="Retrieve SDG predictions for a given SDG, reduction shorthand, and scenario type."
)
async def get_sdg_predictions_for_dimensionality_reductions_with_scenario(
    sdg: int,
    reduction_shorthand: str,
    scenario_type: ScenarioType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGPredictionSchemaFull]:
    try:
        user = verify_token(token, db)

        sdg_predictions = (
            db.query(SDGPrediction)
            .join(DimensionalityReduction, SDGPrediction.publication_id == DimensionalityReduction.publication_id)
            .join(SDGLabelDecision, SDGPrediction.publication_id == SDGLabelDecision.publication_id)  # New join
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                DimensionalityReduction.sdg == sdg,
                SDGPrediction.prediction_model == "Aurora",
                SDGLabelDecision.scenario_type == scenario_type  # Filtering by scenario_type
            )
            .order_by(SDGPrediction.prediction_id)
            # .limit(mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE)
            .all()
        )

        logging.info(f"Retrieved {len(sdg_predictions)} SDG predictions for SDG {sdg}, scenario type '{scenario_type}', and reduction shorthand '{reduction_shorthand}'.")
        logging.info(f"Returning {len(sdg_predictions[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE])} SDG predictions.")

        return sdg_predictions[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching SDG predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching SDG predictions: {e}")


@router.get(
    "/dimensionality-reductions/{reduction_shorthand}/{part_number}/{total_parts}/",
    response_model=List[SDGPredictionSchemaFull],
    description="Retrieve the corresponding SDG predictions for a specific part of dimensionality reductions."
)
async def get_sdg_predictions_for_dimensionality_reductions_partitioned(
    reduction_shorthand: str,
    part_number: int,
    total_parts: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[SDGPredictionSchemaFull]:
    """
    Retrieve the corresponding SDG predictions for a specific part of dimensionality reductions.
    The dimensionality reductions are divided into `total_parts` parts, and the `part_number` specifies which part to retrieve.
    """
    try:
        # Ensure user is authenticated
        user = verify_token(token, db)

        # Validate part_number and total_parts
        if part_number < 1 or part_number > total_parts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"part_number must be between 1 and {total_parts}",
            )

        # Query the total number of dimensionality reductions for the given shorthand
        total_count = db.query(DimensionalityReduction).filter(
            DimensionalityReduction.reduction_shorthand == reduction_shorthand
        ).count()

        logging.debug(f"SDG - Total Count (Dimensionality Reductions): {total_count}")

        if total_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No dimensionality reductions found for shorthand: {reduction_shorthand}",
            )

        # Calculate the start and end indices for the requested part
        part_size = total_count // total_parts
        remainder = total_count % total_parts

        start_index = (part_number - 1) * part_size
        end_index = start_index + part_size

        logging.debug(
            f"SDG - Part Size: {part_size}, Remainder: {remainder}, Start Index: {start_index}, End Index: {end_index}"
        )

        # Adjust for the remainder in the last part
        if part_number == total_parts:
            end_index += remainder

        # Fetch the specific part of dimensionality reductions
        dimensionality_reductions = db.query(DimensionalityReduction).filter(
            DimensionalityReduction.reduction_shorthand == reduction_shorthand
        ).order_by(DimensionalityReduction.dim_red_id).offset(start_index).limit(end_index - start_index).all()

        logging.debug(f"SDG - Dimensionality Reductions: {len(dimensionality_reductions)}")

        # Extract publication IDs from the dimensionality reductions
        publication_ids = [dim_red.publication_id for dim_red in dimensionality_reductions]

        logging.debug(f"SDG - Publications: {len(publication_ids)}")

        if not publication_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No publications found for the specified part of dimensionality reductions.",
            )

        # Fetch the corresponding SDG predictions
        sdg_predictions = db.query(SDGPrediction).filter(
            SDGPrediction.publication_id.in_(publication_ids)
        ).filter(SDGPrediction.prediction_model == sdg_predictions_router_settings.DEFAULT_MODEL).all()

        logging.debug(f"SDG - SDG Predictions: {len(sdg_predictions)}")
        return sdg_predictions
        # return [SDGPredictionSchemaFull.model_validate(pred) for pred in sdg_predictions] # slows it down very hard

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching SDG predictions: {e}",
        )

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
    """
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Extract publication IDs from the request
    publication_ids = request.publications_ids

    # Use MetricsService to calculate metrics
    return metrics_service.get_distribution_metrics_by_publication_ids(publication_ids, db)

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
    """
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Use MetricsService to calculate metrics
    return metrics_service.get_publication_metrics_by_id(publication_id, db)

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
    """
    # Ensure user is authenticated
    user = verify_token(token, db)

    # Use MetricsService to calculate metrics
    return metrics_service.get_publications_by_metric(metric_type, order, top_n, db)

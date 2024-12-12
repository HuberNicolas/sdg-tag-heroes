from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import PublicationQuery, UserCoordinatesRequest
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import DimensionalityReduction, SDGPrediction
from models.publications.publication import Publication
from schemas import DimensionalityReductionSchemaFull
from services.umap_coordinates_generator import UMAPCoordinateService

from settings.settings import DimensionalityReductionsRouterSettings
dimensionality_reductions_router_settings = DimensionalityReductionsRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(dimensionality_reductions_router_settings.DIMENSIONALITYREDUCTIONS_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/dimensionality_reductions",
    tags=["Dimensionality Reductions"],
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
    "/user-coordinates",
    response_model=Dict[str, float],
    description=(
        "Calculate dimensionality reduction using user coordinates."
    ),
)
async def get_dimensionality_reductions_by_sdg_values(
    request: UserCoordinatesRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),

) -> Dict[str, float]:
    umap_service = UMAPCoordinateService()

    coordinates = umap_service.get_coordinates(query=request.user_query, sdg=request.sdg, level=request.level)
    return coordinates




@router.get(
    "/by-sdg-values",
    response_model=Dict[str, Any],  # Returns both statistics and dimensionality reduction data
    description=(
        "Retrieve dimensionality reductions of publications filtered by SDG values within a specified range. "
        "You can specify a fixed model, level, and reduction shorthand for additional filtering."
    ),
)
async def get_dimensionality_reductions_by_sdg_values(
    sdg_range: Tuple[float, float] = Query(..., description="Range for SDG values, e.g., (0.98, 0.99)"),
    limit: int = Query(10, description="Limit for the number of publications per SDG group"),
    sdgs: Optional[List[int]] = Query(None, description="List of specific SDGs to filter, e.g., [1, 3, 12]"),
    model: Optional[str] = Query(None, description="Fixed model name to filter by, e.g., 'Aurora'"),
    level: Optional[List[int]] = Query(None, description="List of levels to filter, e.g., ?level=1&level=2"),
    reduction_shorthand: Optional[str] = Query(None, description="Filter by reduction shorthand, e.g., 'UMAP-15-0.1-2'"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    Retrieve dimensionality reductions of publications filtered by SDG values within a specified range.
    Includes additional filters for levels and reduction shorthand.
    """
    # Verify the token before proceeding
    user = verify_token(token, db)  # Raises HTTPException if the token is invalid or expired

    # Unpack the range
    min_value, max_value = sdg_range

    print(f"Raw SDGs Query Param: {sdgs}")

    # Check if `sdgs` is provided and not empty; otherwise, use the default range
    if sdgs is not None and len(sdgs) > 0:
        sdg_list = sdgs
    else:
        sdg_list = list(range(1, 18))

    # Result dictionary to store dimensionality reductions and statistics
    result = {
        "statistics": {
            "general_range": {"min_value": min_value, "max_value": max_value},
            "sdg_statistics": {}
        },
        "dimensionality_reductions": {}
    }

    for sdg in sdg_list:
        # Construct the base query for publications matching the SDG criteria
        sdg_attr = f"sdg{sdg}"
        query = db.query(Publication).join(SDGPrediction)

        if model:
            # Filter by model and SDG value range
            query = query.filter(
                SDGPrediction.prediction_model == model,
                getattr(SDGPrediction, sdg_attr).between(min_value, max_value)
            )
        else:
            # Filter by SDG value range only
            query = query.filter(getattr(SDGPrediction, sdg_attr).between(min_value, max_value))

        # Order the query by the SDG value in descending order and limit the results
        query = query.order_by(getattr(SDGPrediction, sdg_attr).desc()).limit(limit)

        # Fetch publications
        publications = query.all()

        # Collect statistics
        retrieved_count = len(publications)
        min_pred = float('inf')
        max_pred = float('-inf')
        model_counts = defaultdict(int)

        # Gather dimensionality reductions for the retrieved publications
        dim_reductions = []
        for publication in publications:
            for prediction in publication.sdg_predictions:
                if model and prediction.prediction_model != model:
                    continue
                pred_value = getattr(prediction, sdg_attr)
                min_pred = min(min_pred, pred_value)
                max_pred = max(max_pred, pred_value)
                model_counts[prediction.prediction_model] += 1

            # Add dimensionality reductions associated with this publication and the current SDG
            for dim_red in publication.dimensionality_reductions:
                if dim_red.sdg == sdg:  # Ensure the dimensionality reduction matches the current SDG
                    if level and dim_red.level not in level:
                        continue  # Skip if the level does not match
                    if reduction_shorthand and dim_red.reduction_shorthand != reduction_shorthand:
                        continue  # Skip if the shorthand does not match
                    dim_reductions.append(DimensionalityReductionSchemaFull.model_validate(dim_red))

        # Prepare SDG-specific statistics
        result["statistics"]["sdg_statistics"][f"sdg{sdg}"] = {
            "limit": limit,
            "retrieved_count": retrieved_count,
            "min_pred": min_pred if min_pred != float('inf') else None,
            "max_pred": max_pred if max_pred != float('-inf') else None,
            "pubs_per_model": dict(model_counts)
        }

        # Add dimensionality reductions to result
        result["dimensionality_reductions"][f"sdg{sdg}"] = dim_reductions

    return result





@router.get(
    "/",
    response_model=Dict[str, Any],
    description="Retrieve dimensionality reductions for specific SDGs and levels with optional filters."
)
async def get_dimensionality_reductions(
    sdg: List[int] = Query(..., description="List of specific SDGs to filter, e.g., ?sdg=1&sdg=4&sdg=12"),
    level: List[int] = Query(..., description="List of levels to filter, e.g., ?level=1&level=2&level=3"),
    reduction_shorthand: Optional[str] = Query(None, description="Filter by reduction shorthand, e.g., 'UMAP-15-0.1-2'"),
    limit: int = Query(200, description="Limit the number of results per SDG and level"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Retrieve dimensionality reductions filtered by SDGs, levels, and optional shorthand.
    Returns grouped results for each SDG and level, along with stats.
    """
    result = {"reductions": {}, "stats": {}}

    total_reductions = 0
    sdg_stats = {}

    for sdg_value in sdg:
        sdg_reductions = {}
        sdg_total = 0

        for level_value in level:
            query = db.query(DimensionalityReduction).filter(
                DimensionalityReduction.sdg == sdg_value,
                DimensionalityReduction.level == level_value
            )

            if reduction_shorthand:
                query = query.filter(DimensionalityReduction.reduction_shorthand == reduction_shorthand)

            # Limit results per SDG and level
            query = query.limit(limit)

            # Fetch results
            dim_reductions = query.all()

            # Serialize results
            reductions_data = [
                {
                    "dim_red_id": dr.dim_red_id,
                    "publication_id": dr.publication_id,
                    "reduction_technique": dr.reduction_technique,
                    "reduction_shorthand": dr.reduction_shorthand,
                    "x_coord": dr.x_coord,
                    "y_coord": dr.y_coord,
                    "z_coord": dr.z_coord,
                    "sdg": dr.sdg,
                    "level": dr.level,
                    "created_at": dr.created_at,
                    "updated_at": dr.updated_at,
                }
                for dr in dim_reductions
            ]

            # Add results for the current level
            sdg_reductions[f"level{level_value}"] = reductions_data
            sdg_total += len(dim_reductions)
            total_reductions += len(dim_reductions)

        # Add reductions grouped by SDG
        result["reductions"][f"sdg{sdg_value}"] = sdg_reductions
        sdg_stats[f"sdg{sdg_value}"] = {"total_levels": len(level), "total_reductions": sdg_total}

    # Add stats
    result["stats"] = {
        "total_sdg_groups": len(sdg),
        "total_levels": len(level),
        "total_reductions": total_reductions,
        "sdg_breakdown": sdg_stats,
    }

    return result



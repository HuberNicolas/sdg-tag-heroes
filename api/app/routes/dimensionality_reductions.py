from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload, load_only

from api.app.models.query import PublicationQuery
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from models import DimensionalityReduction



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


@router.get(
    "/",
    response_model=Dict[str, Any],
    description="Retrieve dimensionality reductions for specific SDGs and levels with optional filters."
)
async def get_dimensionality_reductions(
    sdg: List[int] = Query(..., description="List of specific SDGs to filter, e.g., ?sdg=1&sdg=4&sdg=12"),
    level: List[int] = Query(..., description="List of levels to filter, e.g., ?level=1&level=2&level=3"),
    reduction_shorthand: Optional[str] = Query(None, description="Filter by reduction shorthand, e.g., 'UMAP-15-0.1-2'"),
    limit: int = Query(100, description="Limit the number of results per SDG and level"),
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



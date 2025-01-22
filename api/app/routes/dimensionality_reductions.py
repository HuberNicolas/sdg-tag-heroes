from collections import defaultdict
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models import DimensionalityReduction, SDGPrediction
from models.publications.publication import Publication
from requests_models.dimensionality_reductions import UserCoordinatesRequest, \
    DimensionalityReductionPublicationIdsRequest
from schemas import DimensionalityReductionSchemaFull
from schemas.dimensionality_reduction import FilteredDimensionalityReductionStatisticsSchema, \
    FilteredSDGStatisticsSchema, \
    UserCoordinatesSchema, GroupedDimensionalityReductionResponseSchema, GroupedDimensionalityReductionStatisticsSchema, \
    GroupedSDGStatisticsSchema
from services.umap_coordinates_generator import UMAPCoordinateService
from settings.settings import DimensionalityReductionsRouterSettings
from utils.logger import logger

# Setup Logging
dimensionality_reductions_router_settings = DimensionalityReductionsRouterSettings()
logging = logger(dimensionality_reductions_router_settings.DIMENSIONALITYREDUCTIONS_ROUTER_LOG_NAME)

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

# Use the UMAP service to calculate coordinates
umap_service = UMAPCoordinateService()

router = APIRouter(
    prefix="/dimensionality-reductions",
    tags=["Dimensionality Reductions"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get("/", response_model=List[DimensionalityReductionSchemaFull], description="Retrieve all dimensionality reduction results")
async def get_dimensionality_reductions(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[DimensionalityReductionSchemaFull]:
    """
    Retrieve all dimensionality reduction.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        dimensionality_reductions = db.query(DimensionalityReduction).limit(1000).all()

        return [DimensionalityReductionSchemaFull.model_validate(dimensionality_reduction) for dimensionality_reduction in dimensionality_reductions]


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching dimensionality reductions: {e}",
        )

@router.post(
    "/publications/{reduction_shorthand}",
    response_model=List[DimensionalityReductionSchemaFull],
    description="Retrieve all dimensionality reduction results for specified publications."
)
async def get_dimensionality_reductions_for_publications_by_ids(
    request: DimensionalityReductionPublicationIdsRequest,
    reduction_shorthand: str = "UMAP-15-0.1-2",
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[DimensionalityReductionSchemaFull]:
    """
    Retrieve all dimensionality reductions for a specific set of publications.
    """
    try:
        # Ensure user is authenticated
        user = verify_token(token, db)

        # Extract publication IDs from the request
        publication_ids = request.publication_ids

        # Fetch publications matching the provided IDs
        publications = db.query(Publication).filter(
            Publication.publication_id.in_(publication_ids)
        ).all()

        if not publications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No publications found for the given IDs: {publication_ids}",
            )

        # Gather dimensionality reductions for each publication
        dimensionality_reductions = db.query(DimensionalityReduction).filter(
            DimensionalityReduction.publication_id.in_(publication_ids),
            DimensionalityReduction.reduction_shorthand == reduction_shorthand
        ).all()

        # Validate and return dimensionality reductions
        return [
            DimensionalityReductionSchemaFull.model_validate(reduction)
            for reduction in dimensionality_reductions
        ]

    except HTTPException:
        raise  # Re-raise any HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching dimensionality reductions: {e}",
        )

@router.get("/publications/{publication_id}/{reduction_shorthand}", response_model=List[DimensionalityReductionSchemaFull], description="Retrieve all dimensionality reduction results")
async def get_dimensionality_reductions_for_publication(
    publication_id: int,
    reduction_shorthand: str = "UMAP-15-0.1-2",
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[DimensionalityReductionSchemaFull]:
    """
    Retrieve all dimensionality reduction for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        dimensionality_reductions = db.query(DimensionalityReduction).filter(DimensionalityReduction.publication.has(publication_id=publication_id)).filter(DimensionalityReduction.reduction_shorthand == reduction_shorthand).all()

        return [DimensionalityReductionSchemaFull.model_validate(dimensionality_reduction) for dimensionality_reduction in dimensionality_reductions]


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching dimensionality reductions for publication {publication_id}: {e}",
        )

@router.post(
    "/user-coordinates",
    response_model=UserCoordinatesSchema,
    description=(
        "Calculate dimensionality reduction using user coordinates."
    ),
)
async def get_user_coordinates(
    request: UserCoordinatesRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> UserCoordinatesSchema:
    try:
        # Verify the token before proceeding
        user = verify_token(token, db)
        coordinates = umap_service.get_coordinates(
            query=request.user_query, sdg=request.sdg, level=request.level
        )
        return UserCoordinatesSchema.model_validate(coordinates)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while calculating dimensionality reductions: {e}",
        )


@router.get(
    "/filtered",
    response_model=FilteredDimensionalityReductionStatisticsSchema,
    description="Retrieve dimensionality reductions filtered by SDG values and optional parameters."
)
async def get_filtered_dimensionality_reductions(
    sdg_range: Tuple[float, float] = Query(..., description="Range for SDG values, e.g., (0.98, 0.99)"),
    limit: int = Query(10, description="Limit for the number of publications per SDG group"),
    sdgs: Optional[List[int]] = Query(None, description="List of specific SDGs to filter, e.g., [1, 3, 12]"),
    model: Optional[str] = Query(None, description="Fixed model name to filter by, e.g., 'Aurora'"),
    level: Optional[List[int]] = Query(None, description="List of levels to filter, e.g., ?level=1&level=2"),
    reduction_shorthand: Optional[str] = Query(None, description="Filter by reduction shorthand, e.g., 'UMAP-15-0.1-2'"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> FilteredDimensionalityReductionStatisticsSchema:
    """
    Retrieve dimensionality reductions filtered by SDG values within a specified range.
    """
    verify_token(token, db)

    min_value, max_value = sdg_range
    sdg_list = sdgs if sdgs else list(range(1, 18))

    result_statistics = {}
    result_reductions = {}

    for sdg in sdg_list:
        sdg_attr = f"sdg{sdg}"
        query = db.query(Publication).join(SDGPrediction)

        if model:
            query = query.filter(
                SDGPrediction.prediction_model == model,
                getattr(SDGPrediction, sdg_attr).between(min_value, max_value)
            )
        else:
            query = query.filter(getattr(SDGPrediction, sdg_attr).between(min_value, max_value))

        query = query.order_by(getattr(SDGPrediction, sdg_attr).desc()).limit(limit)
        publications = query.all()

        retrieved_count = len(publications)
        min_pred = float('inf')
        max_pred = float('-inf')
        model_counts = defaultdict(int)
        dim_reductions = []

        for publication in publications:
            for sdg_prediction in publication.sdg_predictions:
                if model and sdg_prediction.prediction_model != model:
                    continue
                pred_value = getattr(sdg_prediction, sdg_attr)
                min_pred = min(min_pred, pred_value)
                max_pred = max(max_pred, pred_value)
                model_counts[sdg_prediction.prediction_model] += 1

            for dim_reduction in publication.dimensionality_reductions:
                if dim_reduction.sdg == sdg:
                    if level and dim_reduction.level not in level:
                        continue
                    if reduction_shorthand and dim_reduction.reduction_shorthand != reduction_shorthand:
                        continue
                    dim_reductions.append(DimensionalityReductionSchemaFull.model_validate(dim_reduction))

        result_statistics[f"sdg{sdg}"] = FilteredSDGStatisticsSchema(
            limit=limit,
            retrieved_count=retrieved_count,
            min_prediction_value=min_pred if min_pred != float('inf') else None,
            max_prediction_value=max_pred if max_pred != float('-inf') else None,
            publications_per_model=dict(model_counts),
        )
        result_reductions[f"sdg{sdg}"] = dim_reductions

    return FilteredDimensionalityReductionStatisticsSchema(
        statistics=result_statistics,
        dimensionality_reductions=result_reductions
    )


@router.get(
    "/grouped",
    response_model=GroupedDimensionalityReductionResponseSchema,
    description="Retrieve dimensionality reductions grouped by specific SDGs and levels."
)
async def get_grouped_dimensionality_reductions(
    sdg: List[int] = Query(..., description="List of specific SDGs to filter, e.g., ?sdg=1&sdg=4&sdg=12"),
    level: List[int] = Query(..., description="List of levels to filter, e.g., ?level=1&level=2&level=3"),
    reduction_shorthand: Optional[str] = Query(None, description="Filter by reduction shorthand, e.g., 'UMAP-15-0.1-2'"),
    limit: int = Query(200, description="Limit the number of results per SDG and level"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> GroupedDimensionalityReductionResponseSchema:
    """
    Retrieve dimensionality reductions grouped by SDGs and levels, with optional shorthand filter.
    """
    verify_token(token, db)

    reductions = {}
    sdg_stats = {}
    total_reductions = 0

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

            dim_reductions = query.limit(limit).all()

            # Store results for current level
            sdg_reductions[f"level{level_value}"] = [
                DimensionalityReductionSchemaFull.model_validate(dim_reduction) for dim_reduction in dim_reductions
            ]
            count = len(dim_reductions)
            sdg_total += count
            total_reductions += count

        # Group reductions and stats for current SDG
        reductions[f"sdg{sdg_value}"] = sdg_reductions
        sdg_stats[f"sdg{sdg_value}"] = GroupedSDGStatisticsSchema(
            total_levels=len(level),
            total_reductions=sdg_total
        )

    return GroupedDimensionalityReductionResponseSchema(
        dimensionality_reductions=reductions,
        stats=GroupedDimensionalityReductionStatisticsSchema(
            total_sdg_groups=len(sdg),
            total_levels=len(level),
            total_dimensionality_reductions=total_reductions,
            sdg_breakdown=sdg_stats
        )
    )

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import and_
from sqlalchemy.orm import Session, sessionmaker, aliased

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from db.qdrantdb_connector import client as qdrant_client
from enums.enums import LevelType, ScenarioType
from models import SDGPrediction, SDGLabelDecision, SDGUserLabel
from models.publications.dimensionality_reduction import DimensionalityReduction
from models.publications.publication import Publication
from request_models.publication import PublicationIdsRequest
from request_models.publication_similarity_query_service import PublicationSimilarityQueryRequest
from schemas import PublicationSchemaBase, PublicationSchemaFull
from schemas.services.publication_similarity_query_service import PublicationSimilaritySchema
from services.publication_similarity_query_service import PublicationSimilarityQueryService
from settings.settings import PublicationsRouterSettings, MariaDBSettings
from utils.logger import logger

# Setup Logging
publications_router_settings = PublicationsRouterSettings()
mariadb_settings = MariaDBSettings()
logging = logger(publications_router_settings.PUBLICATIONS_ROUTER_LOG_NAME)

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
    prefix="/publications",
    tags=["Publications"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.post(
    "/",
    response_model=List[PublicationSchemaBase],
    description="Get a list of publications by IDs"
)
async def get_publications_by_ids(
    request: PublicationIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[PublicationSchemaBase]:
    """
    Returns a list of publications by IDs
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        publication_ids = request.publication_ids

        publications = (db.query(Publication)
                        .filter(Publication.publication_id.in_(publication_ids)).all())

        return [PublicationSchemaBase.model_validate(publication) for publication in publications]
    except Exception as e:
        logging.error(f"Error fetching publications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the publications: {e}",
        )


@router.get(
    "/",
    response_model=Page[PublicationSchemaBase],
    description="Get all publications"
)
async def get_publications(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Page[PublicationSchemaBase]:
    """
    Retrieve all publications with optional minimal or full details based on the 'minimal' query parameter.
    Supports pagination.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Base query for fetching publications
        query = db.query(Publication)

        # Use FastAPI Pagination to fetch paginated data
        paginated_query = sqlalchemy_paginate(query)

        paginated_query.items = [PublicationSchemaBase.model_validate(pub) for pub in paginated_query.items]

        return paginated_query

    except Exception as e:
        logging.error(f"Error fetching publications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching publications: {e}",
        )

@router.get(
    "/{publication_id}",
    response_model=PublicationSchemaFull,
    description="Get a single publication by ID"
)
async def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> PublicationSchemaFull:
    """
    Retrieve a single publication by ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query to fetch the publication by ID
        publication = (db.query(Publication)
                       .filter(Publication.publication_id == publication_id).first())

        if not publication:
            logging.warning(f"Publication with ID {publication_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found"
            )

        # Validate and return the full schema
        return PublicationSchemaFull.model_validate(publication)

    except Exception as e:
        logging.error(f"Error fetching publication with ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the publication with ID {publication_id}: {e}",
        )

@router.post(
    "/similar/{top_k}",
    response_model=PublicationSimilaritySchema,
    description="Retrieve publications similar to the user query along with their similarity scores."
)
async def get_similar_publications(
    top_k: int,
    request: PublicationSimilarityQueryRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> PublicationSimilaritySchema:
    """
    Retrieve publications similar to the user query based on vector similarity.
    """
    # Ensure user is authenticated
    verify_token(token, db)

    # Initialize the similarity service
    similarity_service = PublicationSimilarityQueryService(qdrant_client, db)

    # Call the service to get similar publications
    return similarity_service.get_similar_publications(
        user_query=request.user_query,
        top_k=top_k,
        publication_ids=request.publication_ids
    )

@router.get(
    "/dimensionality-reductions/sdgs/{sdg}/{reduction_shorthand}/{level}/",
    response_model=List[PublicationSchemaBase],
    description="Retrieve the corresponding publications for a given SDG, reduction shorthand, and level."
)
async def get_publications_for_dimensionality_reductions(
    sdg: int,
    reduction_shorthand: str,
    level: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[PublicationSchemaBase]:
    try:
        user = verify_token(token, db)

        level_type = {1: LevelType.LEVEL_1, 2: LevelType.LEVEL_2, 3: LevelType.LEVEL_3}.get(level)
        if not level_type:
            raise HTTPException(status_code=400, detail="Invalid level. Must be 1, 2, or 3.")

        min_value, max_value = level_type.min_value, level_type.max_value

        publications = (
            db.query(Publication)
            .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
            .join(DimensionalityReduction, Publication.publication_id == DimensionalityReduction.publication_id)
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                getattr(SDGPrediction, f"sdg{sdg}").between(min_value, max_value),
                SDGPrediction.prediction_model == "Aurora"
            )
            .order_by(Publication.publication_id)
            #.limit(mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE) # THIS DID NO work, much less pubs, idk why
            .all()
        )

        logging.info(f"Retrieved {len(publications)} publications for SDG {sdg}, level {level}, and reduction shorthand '{reduction_shorthand}'.")
        logging.info(f"Returning {len(publications[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE])} publications for SDG {sdg}, level {level}, and reduction shorthand '{reduction_shorthand}'.")

        return publications[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching publications: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching publications: {e}")


@router.get(
    "/dimensionality-reductions/sdgs/{sdg}/{reduction_shorthand}/scenarios/{scenario_type}/",
    response_model=List[PublicationSchemaBase],
    description="Retrieve the corresponding publications for a given SDG, reduction shorthand, and scenario type."
)
async def get_publications_for_dimensionality_reductions_with_scenario(
    sdg: int,
    reduction_shorthand: str,
    scenario_type: ScenarioType,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[PublicationSchemaBase]:
    try:
        user = verify_token(token, db)

        publications = (
            db.query(Publication)
            .join(SDGPrediction, Publication.publication_id == SDGPrediction.publication_id)
            .join(DimensionalityReduction, Publication.publication_id == DimensionalityReduction.publication_id)
            .join(SDGLabelDecision, Publication.publication_id == SDGLabelDecision.publication_id)  # New join
            .filter(
                DimensionalityReduction.reduction_shorthand == reduction_shorthand,
                DimensionalityReduction.sdg == sdg,
                SDGPrediction.prediction_model == "Aurora",
                SDGLabelDecision.scenario_type == scenario_type  # Filtering by scenario_type
            )
            .order_by(Publication.publication_id)
            # .limit(mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE)
            .all()
        )

        logging.info(f"Retrieved {len(publications)} publications for SDG {sdg}, scenario type '{scenario_type}', and reduction shorthand '{reduction_shorthand}'.")
        logging.info(f"Returning {len(publications[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE])} publications.")

        return publications[0:mariadb_settings.DEFAULT_SDG_EXPLORATION_SIZE]
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching publications: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching publications: {e}")

@router.get(
    "/dimensionality-reductions/{reduction_shorthand}/{part_number}/{total_parts}/",
    response_model=List[PublicationSchemaBase],
    description="Retrieve the corresponding publications for a specific part of dimensionality reductions."
)
async def get_publications_for_dimensionality_reductions_partitioned(
    reduction_shorthand: str,
    part_number: int,
    total_parts: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[PublicationSchemaBase]:
    """
    Retrieve the corresponding publications for a specific part of dimensionality reductions.
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

        logging.debug(f"P - Total Count (Dimensionality Reductions): {total_count}")

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
            f" P - Part Size: {part_size}, Remainder: {remainder}, Start Index: {start_index}, End Index: {end_index}")

        # Adjust for the remainder in the last part
        if part_number == total_parts:
            end_index += remainder

        # Fetch the specific part of dimensionality reductions
        dimensionality_reductions = db.query(DimensionalityReduction).filter(
            DimensionalityReduction.reduction_shorthand == reduction_shorthand
        ).order_by(DimensionalityReduction.dim_red_id).offset(start_index).limit(end_index - start_index).all()

        logging.debug(f"P - Dimensionality Reductions: {len(dimensionality_reductions)}")

        # Extract publication IDs from the dimensionality reductions
        publication_ids = [dim_red.publication_id for dim_red in dimensionality_reductions]

        logging.debug(f"P - Publications: {len(publication_ids)}")

        if not publication_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No publications found for the specified part of dimensionality reductions.",
            )

        # Fetch the corresponding publications
        publications = db.query(Publication).filter(
            Publication.publication_id.in_(publication_ids)
        ).all()
        return publications
        # return [PublicationSchemaFull.model_validate(pub) for pub in publications] # slows it down very hard

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching publications: {e}",
        )


@router.get(
    "/scenarios/{scenario_type}/{top_k}",
    response_model=List[PublicationSchemaBase],
    description="Retrieve publications associated with a specific scenario type."
)
async def get_publications_by_scenario(
    scenario_type: ScenarioType,
    top_k: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[PublicationSchemaBase]:
    """
    Retrieve publications associated with a specific scenario type.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        publications = (
            db.query(Publication)
            .join(SDGLabelDecision, Publication.publication_id == SDGLabelDecision.publication_id)
            .filter(SDGLabelDecision.scenario_type == scenario_type)
            .order_by(Publication.publication_id)
            .limit(top_k)
        )

        if not publications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No publications found for scenario type {scenario_type}",
            )

        return [PublicationSchemaBase.model_validate(pub) for pub in publications]

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching publications for scenario type {scenario_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching publications for scenario type {scenario_type}: {e}",
        )


@router.get(
    "/users/{user_id}/labeled",
    response_model=List[PublicationSchemaBase],
    description="Get all publications labeled by a specific user"
)
async def get_user_labeled_publications(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[PublicationSchemaBase]:
    """
    Retrieve all publications that a specific user has labeled.
    """
    try:
        # Ensure user is authenticated
        user = verify_token(token, db)

        # Fetch all publications the user has labeled
        publications = (
            db.query(Publication)
            .join(SDGUserLabel, Publication.publication_id == SDGUserLabel.publication_id)
            .filter(SDGUserLabel.user_id == user_id)
            .all()
        )

        if not publications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No labeled publications found for user ID {user_id}",
            )

        return [PublicationSchemaBase.model_validate(pub) for pub in publications]

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching labeled publications for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching labeled publications for user {user_id}: {e}",
        )

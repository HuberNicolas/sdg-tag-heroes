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
from models.publications.author import Author
# Import models
from models.publications.publication import Publication
from schemas.publications.author import AuthorSchemaBase, AuthorSchemaFull

from schemas.publications.publication import PublicationSchemaBase, PublicationSchemaFull



from services.gpt_explainer import SDGExplainer

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
    "/{publication_id}/authors/{author_id}",
    response_model=AuthorSchemaFull,
    description="Retrieve a specific author associated with a specific publication"
)
async def get_publication_author(
    publication_id: int,
    author_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> AuthorSchemaFull:
    """
    Retrieve a specific author for a specific publication.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        # Query the database for the publication
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Check if the author is associated with the publication
        author = next((author for author in publication.authors if author.author_id == author_id), None)

        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_id} not associated with publication ID {publication_id}",
            )

        # Return the detailed information of the specific author
        return AuthorSchemaFull.model_validate(author)

    except Exception as e:
        logging.error(f"Error fetching author ID {author_id} for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the author for the publication",
        )


@router.get(
    "/{publication_id}/authors",
    response_model=List[AuthorSchemaBase],
    description="Retrieve all authors associated with a specific publication"
)
async def get_publication_authors(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[AuthorSchemaBase]:
    """
    Retrieve all authors for a specific publication.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        # Query the database for the publication and its authors
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Return the list of authors associated with the publication
        return [AuthorSchemaBase.model_validate(author) for author in publication.authors]

    except Exception as e:
        logging.error(f"Error fetching authors for publication ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching authors for the publication",
        )

@router.get(
    "/by-sdg-values",
    response_model=Dict[str, Any],  # Returns both statistics and publication data
    description=(
        "Retrieve publications filtered by SDG values within a specified range. "
        "You can specify a fixed model when multiple models are available."
    ),
)
async def get_publications_by_sdg_values(
    sdg_range: Tuple[float, float] = Query(..., description="Range for SDG values, e.g., (0.98, 0.99)"),
    limit: int = Query(10, description="Limit for the number of publications per SDG group"),
    sdgs: Optional[List[int]] = Query(None, description="List of specific SDGs to filter, e.g., [1, 3, 12]"),
    model: Optional[str] = Query(None, description="Fixed model name to filter by, e.g., 'model_A'"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:
    """
    Retrieve publications filtered by SDG values within a specified range.
    Always returns the full model with all related data included.
    """
    # Verify the token before proceeding
    user = verify_token(token)  # Raises HTTPException if the token is invalid or expired

    # Unpack the range
    min_value, max_value = sdg_range

    # Default to all 17 SDGs if none are specified
    sdg_list = sdgs if sdgs else range(1, 18)

    # Result dictionary to store publications and statistics
    result = {
        "statistics": {
            "general_range": {"min_value": min_value, "max_value": max_value},
            "sdg_statistics": {}
        },
        "publications": {}
    }

    for sdg in sdg_list:
        # Construct the base query for the SDG, joining with SDGPrediction
        query = db.query(Publication).join(SDGPrediction)

        # Filter the SDGPrediction objects
        sdg_attr = f"sdg{sdg}"
        if model:
            # If a model is specified, filter by model and SDG value range
            query = query.filter(
                SDGPrediction.prediction_model == model,
                getattr(SDGPrediction, sdg_attr).between(min_value, max_value)
            )
        else:
            # No model specified: Filter by SDG value range
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

        # Convert each publication to the full Pydantic model and update statistics
        full_publications = []
        for publication in publications:
            for prediction in publication.sdg_predictions:
                if model and prediction.prediction_model != model:
                    continue
                pred_value = getattr(prediction, sdg_attr)
                min_pred = min(min_pred, pred_value)
                max_pred = max(max_pred, pred_value)
                model_counts[prediction.prediction_model] += 1

            # Add the full publication model
            full_publications.append(PublicationSchemaFull.model_validate(publication))

        # Prepare SDG-specific statistics
        result["statistics"]["sdg_statistics"][f"sdg{sdg}"] = {
            "limit": limit,
            "retrieved_count": retrieved_count,
            "min_pred": min_pred if min_pred != float('inf') else None,
            "max_pred": max_pred if max_pred != float('-inf') else None,
            "pubs_per_model": dict(model_counts)
        }

        # Add publications to result
        result["publications"][f"sdg{sdg}"] = full_publications

    return result


@router.get(
    "/",
    response_model=Page[Union[PublicationSchemaFull]],
    description="Get all publications"
)
async def get_publications(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Page[PublicationSchemaFull]:
    """
    Retrieve all publications with optional minimal or full details based on the 'minimal' query parameter.
    Supports pagination.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated
        # Base query for fetching publications
        query = db.query(Publication)

        # Use FastAPI Pagination to fetch paginated data
        paginated_query = sqlalchemy_paginate(query)

        paginated_query.items = [PublicationSchemaFull.model_validate(pub) for pub in paginated_query.items]

        return paginated_query

    except Exception as e:
        logging.error(f"Error fetching publications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching publications",
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
        user = verify_token(token)  # Ensure user is authenticated

        # Query to fetch the publication by ID
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        # If not found, raise 404 error
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
            detail="An error occurred while fetching the publication",
        )


@router.get("/{publication_id}/explain/goal/{sdg_id}", response_model=dict,
            description="Explain the relevance of a publication to a specific SDG")
async def explain_publication_sdg_relevance(publication_id: int, sdg_id: int, db: Session = Depends(get_db),
                                            token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_token(token)  # Ensure user is authenticated
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    # Here you would integrate with your SDG explanation service
    explanation = SDGExplainer().explain(publication, goal=str(sdg_id))

    return {"publication_id": publication_id, "sdg_id": sdg_id, "explanation": explanation}


@router.get("/{publication_id}/explain/target/{target_id}", response_model=dict,
            description="Explain the relevance of a publication to a specific SDG target")
async def explain_publication_sdg_target(publication_id: int, target_id: str, db: Session = Depends(get_db),
                                         token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_token(token)  # Ensure user is authenticated
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")

    target_explanation = SDGExplainer().explain(publication,
                                                target=target_id)

    return {"publication_id": publication_id, "target_id": target_id, "explanation": target_explanation}

@router.get("/{publication_id}/keywords", response_model=dict, description="Extract keywords from a publication")
async def extract_keywords(publication_id: int, db: Session = Depends(get_db),
                           token: str = Depends(oauth2_scheme)) -> dict:
    user = verify_token(token)  # Ensure user is authenticated
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found")


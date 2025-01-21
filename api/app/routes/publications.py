from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy.orm import Session, sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from models.publications.publication import Publication
from requests_models.publication import PublicationIdsRequest
from schemas import PublicationSchemaBase, PublicationSchemaFull
from api.app.routes.authentication import verify_token
from api.app.security import Security
from settings.settings import PublicationsRouterSettings
from utils.logger import logger

# Setup Logging
publications_router_settings = PublicationsRouterSettings()
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
    tags=["publications"],
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

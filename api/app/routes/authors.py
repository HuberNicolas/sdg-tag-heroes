from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

# Import models
from models.publications.author import Author
from schemas.publications.author import AuthorSchemaBase, AuthorSchemaFull

from settings.settings import AuthorsRouterSettings
authors_router_settings = AuthorsRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(authors_router_settings.AUTHORS_ROUTER_LOG_NAME)

router = APIRouter(
    prefix="/authors",
    tags=["Authors"],
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
    "/", description="Get all authors (minimal or full detail)"
)
async def get_all_authors(
    minimal: Optional[bool] = Query(False, description="Set to true for minimal response"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Page:
    """
    Retrieve all authors. Responds with a minimal or full response based on the 'minimal' query parameter.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        logging.info(f"Fetching all authors with minimal={minimal}")

        # Base query
        query = db.query(Author)

        # Fetch paginated authors
        authors = paginate(query.order_by(Author.author_id))

        # Adjust schema based on the 'minimal' flag
        if minimal:
            # Transform to minimal schema
            authors.items = [AuthorSchemaBase.from_orm(author) for author in authors.items]
            logging.info("Returning minimal response")
        else:
            # Transform to full schema
            authors.items = [AuthorSchemaFull.from_orm(author) for author in authors.items]
            logging.info("Returning full response")

        return authors

    except Exception as e:
        logging.error(f"Error fetching authors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching authors",
        )

@router.get(
    "/{author_id}",
    description="Get single author by ID (minimal or full detail)"
)
async def get_author(
    author_id: int,
    minimal: Optional[bool] = Query(False, description="Set to true for minimal response"),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Retrieve a single author by ID. Responds with minimal or full details based on the 'minimal' query parameter.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated
        logging.info(f"Fetching author with ID: {author_id}, minimal={minimal}")

        # Query the database for the author
        author = db.query(Author).filter(Author.author_id == author_id).first()

        if not author:
            logging.warning(f"No author found with ID: {author_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
            )

        # Return minimal or full detail based on the 'minimal' flag
        if minimal:
            response = AuthorSchemaBase.from_orm(author)
            logging.info(f"Returning minimal response for author ID: {author_id}")
        else:
            response = AuthorSchemaFull.from_orm(author)
            logging.info(f"Returning full response for author ID: {author_id}")

        return response

    except Exception as e:
        logging.error(f"Error fetching author with ID {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the author",
        )


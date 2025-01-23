from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_pagination
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models.publications.author import Author
from models.publications.publication import Publication
from schemas import AuthorSchemaFull
from settings.settings import AuthorsRouterSettings
from utils.logger import logger

# Setup OAuth2 and security
security = Security()
oauth2_scheme = security.oauth2_scheme

# Setup Logging
authors_router_settings = AuthorsRouterSettings()
logging = logger(authors_router_settings.AUTHORS_ROUTER_LOG_NAME)

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
    prefix="/authors",
    tags=["Authors"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get(
    "/", description="Get all authors (minimal or full detail)"
)
async def get_authors(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Page[AuthorSchemaFull]:
    """
    Retrieve all authors. Responds with a minimal or full response based on the 'minimal' query parameter.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Base query
        query = db.query(Author)

        # Use FastAPI Pagination to fetch paginated data
        paginated_query = sqlalchemy_pagination(query)

        paginated_query.items = [AuthorSchemaFull.model_validate(author) for author in paginated_query.items]

        return paginated_query

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
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Retrieve a single author by ID. Responds with minimal or full details based on the 'minimal' query parameter.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the author
        author = db.query(Author).filter(Author.author_id == author_id).first()

        if not author:
            logging.warning(f"No author found with ID: {author_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
            )

        return AuthorSchemaFull.model_validate(author)

    except Exception as e:
        logging.error(f"Error fetching author with ID {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the author",
        )

@router.get(
    "/publications/{publication_id}",
    response_model=List[AuthorSchemaFull],
    description="Retrieve all authors associated with a specific publication"
)
async def get_publication_authors(
    publication_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> List[AuthorSchemaFull]:
    """
    Retrieve all authors for a specific publication.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query the database for the publication and its authors
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()

        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {publication_id} not found",
            )

        # Return the list of authors associated with the publication
        return [AuthorSchemaFull.model_validate(author) for author in publication.authors]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching authors for the publication",
        )

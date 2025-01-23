from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_pagination

from models.publications.author import Author
from schemas import AuthorSchemaFull
from utils.logger import logger
from settings.settings import AuthorsRouterSettings

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


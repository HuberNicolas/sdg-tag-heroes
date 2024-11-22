from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

# Import models
from models.publications.publication import Publication
from models.publications.author import Author


from schemas.publication import PublicationSchema, FacultySchemaFull, FacultySchemaBase, InstituteSchemaFull, InstituteSchemaBase, DivisionSchemaFull, DivisionSchemaBase, \
    AuthorSchemaBase, AuthorSchemaFull, DimRedSchemaFull, DimRedSchemaBase, SDGPredictionSchemaBase, SDGPredictionSchemaFull


from schemas.publication import AuthorSchemaFull

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
    tags=["authors"],
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
    "/", response_model=List[AuthorSchemaFull], description="Get all authors"
)
async def get_all_authors(db: Session = Depends(get_db)):
    try:
        logging.info("Fetching all authors")

        # Perform a simple SELECT query to fetch all authors
        authors = db.query(Author).all()

        if not authors:
            logging.warning("No publications found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No authors found"
            )

        logging.info(f"Retrieved {len(authors)} authors")

        # Use jsonable_encoder to ensure SQLAlchemy objects are converted into JSON-compatible data
        return JSONResponse(content=jsonable_encoder(authors))
    except Exception as e:
        logging.error(f"Error fetching authors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching authors",
        )

@router.get("/{author_id}", response_model=AuthorSchemaFull, description="Get single author by ID")
async def get_author(author_id: int, db: Session = Depends(get_db)):
    try:
        logging.info(f"Fetching publication with ID: {author_id}")

        # Perform a SELECT query to fetch the publication by ID
        author = db.query(Author).filter(Author.author_id == author_id).first()

        if not author:
            logging.warning(f"No publication found with ID: {author_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
            )

        logging.info(f"Retrieved author with ID: {author_id}")

        # Use jsonable_encoder to ensure SQLAlchemy objects are converted into JSON-compatible data
        return JSONResponse(content=jsonable_encoder(author))
    except Exception as e:
        logging.error(f"Error fetching author with ID {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the author",
        )

@router.get("/{author_id}/publications", response_model=Page[PublicationSchema], description="Get all publications from an author by ID")
async def get_publications_for_author(author_id: int, include: Optional[str] = Query(None), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme))  -> Page[PublicationSchema]:
    # Verify the token before proceeding
    user = verify_token(token)  # This will raise HTTPException if the token is invalid or expired

    try:
        logging.info(f"Fetching publications for author with ID: {author_id}")

        # Query the author along with their publications using joinedload
        author = db.query(Author).filter(Author.author_id == author_id).first()

        if not author:
            logging.warning(f"No author found with ID: {author_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Author not found"
            )

        # Parse the include parameter (example: 'include=division,institute')
        includes = include.split(",") if include else []

        # Paginate publications for the author
        query = db.query(Publication).filter(Publication.authors.any(Author.author_id == author_id))

        # Apply pagination
        publications = paginate(query)

        # Fetched everything, fully hydration

        # Conditionally replace full schema with base schema if keyword is not present:
        for publication in publications.items:
            if 'authors' not in includes and publication.authors:
                publication.authors = [AuthorSchemaBase.from_orm(author) for author in publication.authors]
            if 'faculty' not in includes and publication.faculty:
                publication.faculty = FacultySchemaBase.from_orm(publication.faculty)
            if 'institute' not in includes and publication.institute:
                publication.institute = InstituteSchemaBase.from_orm(publication.institute)
            if 'division' not in includes and publication.division:
                publication.division = DivisionSchemaBase.from_orm(publication.division)
            if 'sdg_predictions' not in includes and publication.sdg_predictions:
                publication.sdg_predictions = SDGPredictionSchemaBase.from_orm(publication.sdg_predictions)
            if 'dim_red' not in includes and publication.dim_red:
                publication.dim_red = DimRedSchemaBase.from_orm(publication.dim_red)
        return publications

    except Exception as e:
        logging.error(f"Error fetching publications for author with ID {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the publications",
        )


from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.models.query import PublicationQuery
from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

# Import models
# Load all of them to prevent the circular error issues
from models.publication import Publication
from models.author import Author
from models.faculty import Faculty
from models.institute import Institute
from models.division import Division
from models.sdg_prediction import SDGPrediction
from models.dim_red import DimRed
from models.sdg_prediction import SDGPrediction
from models.sdg_label import SDGLabel
from models.sdg_label_history import SDGLabelHistory
from models.sdg_label_decision import SDGLabelDecision
from models.sdg_user_label import SDGUserLabel


from schemas.publication import PublicationSchema, FacultySchemaFull, FacultySchemaBase, InstituteSchemaFull, InstituteSchemaBase, DivisionSchemaFull, DivisionSchemaBase, \
    AuthorSchemaBase, AuthorSchemaFull, DimRedSchemaFull, DimRedSchemaBase, SDGPredictionSchemaBase, SDGPredictionSchemaFull

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


@router.post(
    "/", description="Post Publications", response_model=List[PublicationSchema]
)
def post_publications(
    query: PublicationQuery,
    db: Session = Depends(get_db),
):
    logging.info("Fetching publications with filters: %s", query)

    # Start with the base query
    query_filter = db.query(Publication)

    # Apply filters
    if query.title:
        query_filter = query_filter.filter(Publication.title.ilike(f"%{query.title}%"))

    if query.author_name:
        query_filter = query_filter.join(Publication.authors).filter(
            Author.name.ilike(f"%{query.author_name}%")
        )

    if query.year:
        query_filter = query_filter.filter(Publication.year == query.year)

    if query.faculty_id:
        query_filter = query_filter.filter(Publication.faculty_id == query.faculty_id)

    # Execute the query
    publications = query_filter.all()

    if not publications:
        logging.warning("No publications found for the provided filters")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No publications found"
        )

    logging.info(f"Returning {len(publications)} publications")

    # Use jsonable_encoder to ensure SQLAlchemy objects are converted into JSON-compatible data
    return JSONResponse(content=jsonable_encoder(publications))


@router.get(
    "/", response_model=Page[PublicationSchema], description="Get all publications"
)
async def get_publications(include: Optional[str] = Query(None), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Page[PublicationSchema]:
    # Verify the token before proceeding
    user = verify_token(token)  # This will raise HTTPException if the token is invalid or expired

    logging.info("Fetching all publications")

    # Base query for fetching publications
    query = db.query(Publication)

    # Parse the include parameter (example: 'include=division,institute')
    includes = include.split(",") if include else []

    # Conditionally join related tables based on 'include' parameter
    if 'authors' in includes:
        query = query.options(joinedload(Publication.authors))
    if 'faculty' in includes or not includes:
        query = query.options(joinedload(Publication.faculty))
    if 'institute' in includes or not includes:
        query = query.options(joinedload(Publication.institute))
    if 'division' in includes or not includes:
        query = query.options(joinedload(Publication.division))
    if 'sdg_predictions' in includes or not includes:
        query = db.query(Publication).join(SDGPrediction).options(joinedload(Publication.sdg_predictions))
    if 'dim_red' in includes or not includes:
        query = query.options(joinedload(Publication.dim_red))

    # Fetch paginated data
    publications = paginate(query.order_by(Publication.created_at))

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
            print(publication.sdg_predictions)
            publication.sdg_predictions = [SDGPredictionSchemaBase.from_orm(prediction) for prediction in publication.sdg_predictions]
        if 'dim_red' not in includes and publication.dim_red:
            publication.dim_red = DimRedSchemaBase.from_orm(publication.dim_red)
    return publications

@router.get("/{publication_id}", response_model=PublicationSchema, description="Get single publication by ID")
async def get_publication(publication_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> PublicationSchema:
    # Verify the token before proceeding
    user = verify_token(token)  # This will raise HTTPException if the token is invalid or expired
    try:
        logging.info(f"Fetching publication with ID: {publication_id}")
        # Perform a SELECT query to fetch the publication by ID
        publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
        if not publication:
            logging.warning(f"No publication found with ID: {publication_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Publication not found"
            )
        logging.info(f"Retrieved publication with ID: {publication_id}")
        # FastAPI will automatically serialize this to JSON using the response_model
        return publication
    except Exception as e:
        logging.error(f"Error fetching publication with ID {publication_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the publication",
        )

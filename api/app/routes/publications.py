from typing import List, Optional, Dict, Tuple

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
            publication.sdg_predictions = [SDGPredictionSchemaBase.from_orm(prediction) for prediction in publication.sdg_predictions]
        if 'dim_red' not in includes and publication.dim_red:
            publication.dim_red = DimRedSchemaBase.from_orm(publication.dim_red)
    return publications

@router.get(
    "/by-sdg-values",
    response_model=Dict[str, List[PublicationSchema]],
    description=(
        "Retrieve publications filtered by SDG values within a specified range. "
        "You can specify a fixed model or choose a strategy ('highest' or 'lowest') "
        "to select the SDG value when multiple models are available."
    ),
)
async def get_publications_by_sdg_values(
    sdg_range: Tuple[float, float] = Query(..., description="Range for SDG values, e.g., (0.98, 0.99)"),
    limit: int = Query(10, description="Limit for the number of publications per SDG group"),
    sdgs: Optional[List[int]] = Query(None, description="List of specific SDGs to filter, e.g., [1, 3, 12]"),
    include: Optional[str] = Query(None, description="Comma-separated list of related entities to include, e.g., 'authors,faculty'"),
    model: Optional[str] = Query(None, description="Fixed model name to filter by, e.g., 'model_A'"),
    value_strategy: Optional[str] = Query(
        None,
        description="Strategy to select SDG value when multiple models are available: 'highest' or 'lowest'"
    ),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Dict[str, List[PublicationSchema]]:
    # Verify the token before proceeding
    user = verify_token(token)  # Raises HTTPException if the token is invalid or expired

    # Unpack the range
    min_value, max_value = sdg_range

    # Default to all 17 SDGs if none are specified
    sdg_list = sdgs if sdgs else range(1, 18)

    # Parse the include parameter for related entity hydration
    includes = include.split(",") if include else []

    # Result dictionary to store publications for each SDG
    result = {}

    for sdg in sdg_list:
        # Construct the base query for the SDG
        query = db.query(Publication).join(SDGPrediction)

        if value_strategy:
            # Advanced strategy to select 'highest' or 'lowest' SDG value
            if value_strategy == "highest":
                query = query.filter(
                    getattr(SDGPrediction, f"sdg{sdg}") == db.query(SDGPrediction)
                    .filter(SDGPrediction.publication_id == Publication.publication_id)
                    .order_by(getattr(SDGPrediction, f"sdg{sdg}").desc())
                    .limit(1)
                    .subquery().c[f"sdg{sdg}"]
                )
            elif value_strategy == "lowest":
                query = query.filter(
                    getattr(SDGPrediction, f"sdg{sdg}") == db.query(SDGPrediction)
                    .filter(SDGPrediction.publication_id == Publication.publication_id)
                    .order_by(getattr(SDGPrediction, f"sdg{sdg}").asc())
                    .limit(1)
                    .subquery().c[f"sdg{sdg}"]
                )
        elif model:
            # Default behavior: filter by a specified model
            query = query.filter(SDGPrediction.prediction_model == model)

        # Further filter by SDG value range
        query = query.filter(getattr(SDGPrediction, f"sdg{sdg}").between(min_value, max_value))
        query = query.order_by(Publication.created_at).limit(limit)

        # Apply joinedload options for related entities based on 'include' parameter
        if 'authors' in includes:
            query = query.options(joinedload(Publication.authors))
        if 'faculty' in includes or not includes:
            query = query.options(joinedload(Publication.faculty))
        if 'institute' in includes or not includes:
            query = query.options(joinedload(Publication.institute))
        if 'division' in includes or not includes:
            query = query.options(joinedload(Publication.division))
        # Always hydrate the selected `sdg_predictions`
        query = query.options(joinedload(Publication.sdg_predictions))
        if 'dim_red' in includes or not includes:
            query = query.options(joinedload(Publication.dim_red))

        # Fetch publications
        publications = query.all()

        # Convert each publication to a Pydantic model, simplifying related data if necessary
        hydrated_publications = []
        for publication in publications:
            # Create a copy of the publication's data in a way that does not modify the original ORM object
            publication_data = PublicationSchema.from_orm(publication)

            # Select only the relevant SDGPrediction based on model or strategy
            if publication_data.sdg_predictions:
                if model:
                    # Filter by the specified model
                    publication_data.sdg_predictions = [
                        prediction for prediction in publication_data.sdg_predictions if
                        prediction.prediction_model == model
                    ]
                elif value_strategy in ["highest", "lowest"]:
                    # Sort and select the first prediction based on strategy
                    sdg_attr = f"sdg{sdg}"
                    publication_data.sdg_predictions = sorted(
                        publication_data.sdg_predictions,
                        key=lambda p: getattr(p, sdg_attr),
                        reverse=(value_strategy == "highest")
                    )[:1]  # Take only the top prediction

            # Conditionally simplify related data
            if 'authors' not in includes and publication_data.authors:
                publication_data.authors = [AuthorSchemaBase.from_orm(author) for author in publication.authors]
            if 'faculty' not in includes and publication_data.faculty:
                publication_data.faculty = FacultySchemaBase.from_orm(publication.faculty)
            if 'institute' not in includes and publication_data.institute:
                publication_data.institute = InstituteSchemaBase.from_orm(publication.institute)
            if 'division' not in includes and publication_data.division:
                publication_data.division = DivisionSchemaBase.from_orm(publication.division)
            if 'dim_red' not in includes and publication_data.dim_red:
                publication_data.dim_red = DimRedSchemaBase.from_orm(publication.dim_red)

            # Add the hydrated publication data to the result list
            hydrated_publications.append(publication_data)

        # Add to result
        result[f"sdg{sdg}"] = hydrated_publications

    return result



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

    keywords = SDGExplainer().extract_keywords(publication.title,
                                               publication.description)

    return {"publication_id": publication_id, "keywords": keywords}


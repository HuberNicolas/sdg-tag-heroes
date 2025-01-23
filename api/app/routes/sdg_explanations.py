from fastapi import APIRouter, Depends, HTTPException
from pymongo.synchronous.database import Database
from sqlalchemy.orm import Session, sessionmaker

from api.app.routes.authentication import verify_token
from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from db.mongodb_connector import get_explanations_db
from models.publications.publication import Publication
from schemas.sdg_explanations import ExplanationSchema
from settings.settings import ExplanationsRouterSettings, MongoDBSDGSettings
from utils.logger import logger

# Setup Logging
explanations_router_settings = ExplanationsRouterSettings()
logging = logger(explanations_router_settings.EXPLANATIONS_ROUTER_LOG_NAME)

mongo_db_settings = MongoDBSDGSettings()

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


router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get(
    "/publications/{publication_id}",
    response_model=ExplanationSchema,
    description="Get a single SHAP explanation by publication ID"
)
async def get_sdg_explanation(
    publication_id: int,
    db: Session = Depends(get_db),
    mongo_db: Database = Depends(get_explanations_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Fetch SHAP explanations for a given publication ID by first querying the publications table.
    """

    user = verify_token(token, db) # Ensure user is authenticated

    # Query publications table
    publication = db.query(Publication).filter(Publication.publication_id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found in the database.")

    # Use the oai_identifier to query the MongoDB explanations collection
    oai_identifier = publication.oai_identifier
    explanations_collection = mongo_db[mongo_db_settings.DB_COLLECTION_NAME]
    explanation = explanations_collection.find_one({"id": oai_identifier})
    explanation["mongodb_id"] = str(explanation.pop("_id"))
    explanation["oai_identifier"] = oai_identifier
    explanation["sql_id"] = publication_id

    # Lifesaver for index creation, can also be done in Mongodb directly
    #indexes = explanations_collection.index_information()
    #explanations_collection.create_index("id", unique=True)

    if not explanation:
        raise HTTPException(status_code=404, detail="Explanation not found for the given publication.")

    return explanation




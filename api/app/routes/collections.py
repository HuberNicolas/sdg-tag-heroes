from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from models.collection import Collection
from schemas import CollectionSchemaFull
from api.app.routes.authentication import verify_token
from api.app.security import Security
from settings.settings import CollectionsRouterSettings
from utils.logger import logger

# Setup Logging
collections_router_settings = CollectionsRouterSettings()
logging = logger(collections_router_settings.COLLECTIONS_ROUTER_LOG_NAME)

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
    prefix="/collections",
    tags=["collections"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get(
    "/",
    response_model=List[CollectionSchemaFull],
    description="Get all collections"
)
async def get_collections(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[CollectionSchemaFull]:
    """
    Retrieve all collections
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Base query for fetching collections
        collections = db.query(Collection).all()

        # Convert the collection instances to a dictionary
        return [CollectionSchemaFull.model_validate(collection.to_dict()) for collection in collections]

    except Exception as e:
        logging.error(f"Error fetching collections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching collections: {e}",
        )

@router.get(
    "/{collection_id}",
    response_model=CollectionSchemaFull,
    description="Get a single collection by ID"
)
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> CollectionSchemaFull:
    """
    Retrieve a single collection by ID.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query to fetch the collection by ID
        collection = (db.query(Collection)
                       .filter(Collection.collection_id == collection_id).first())

        if not collection:
            logging.warning(f"Collection with ID {collection_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with ID {collection_id} not found"
            )

        # Convert the collection instance to a dictionary
        collection_dict = collection.to_dict()

        # Validate and return the full schema
        return CollectionSchemaFull.model_validate(collection_dict)


    except Exception as e:
        logging.error(f"Error fetching collection with ID {collection_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the collection with ID {collection_id}: {e}",
        )

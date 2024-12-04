from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from models.sdg.sdg_goal import SDGGoal

from schemas.sdg.goal import SDGGoalSchemaFull

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from settings.settings import SDGsRouterSettings
sdgs_router_settings = SDGsRouterSettings()

security = Security()
# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme

# Setup Logging
from utils.logger import logger
logging = logger(sdgs_router_settings.SDGS_ROUTER_LOG_NAME)


router = APIRouter(
    prefix="/sdgs",
    tags=["sdgs"],
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
    "/{sdg_id}",
    response_model=SDGGoalSchemaFull,
    description="Get a single SDG goal by ID with optional inclusion of targets"
)
async def get_sdg(
    sdg_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> SDGGoalSchemaFull:
    """
    Retrieve a single SDG goal by its ID with optional inclusion of targets.
    """
    try:
        # Authenticate user
        user = verify_token(token, db)
        logging.info(f"Fetching SDG goal with ID: {sdg_id}")

        # Base query for fetching the SDG goal
        query = db.query(SDGGoal)
        query = query.options(joinedload(SDGGoal.sdg_targets))

        # Fetch the goal by ID
        sdg_goal = query.filter(SDGGoal.id == sdg_id).first()

        if not sdg_goal:
            logging.warning(f"No SDG goal found with ID: {sdg_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SDG goal not found")

        logging.info(f"Returning SDG goal with ID: {sdg_id}")
        return SDGGoalSchemaFull.model_validate(sdg_goal)

    except Exception as e:
        logging.error(f"Error fetching SDG goal with ID {sdg_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the SDG goal",
        )

@router.get(
    "/",
    response_model=Page[SDGGoalSchemaFull],
    description="Get all SDG goals with optional inclusion of targets"
)
async def get_sdgs(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Retrieve all SDG goals with optional inclusion of targets.
    Supports pagination.
    """
    try:
        # Authenticate user
        user = verify_token(token, db)
        logging.info("Fetching all SDG goals")

        # Base query for SDG goals
        query = db.query(SDGGoal)

        # Use FastAPI Pagination to fetch paginated data
        paginated_query = sqlalchemy_paginate(query)

        # Map the paginated items to Pydantic models
        paginated_query.items = [SDGGoalSchemaFull.model_validate(goal) for goal in paginated_query.items]

        return paginated_query

    except Exception as e:
        logging.error(f"Error fetching SDG goals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching SDG goals",
        )






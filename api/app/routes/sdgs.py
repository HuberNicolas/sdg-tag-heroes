from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine
from models.sdgs.goal import SDGGoal
from schemas.sdgs.goal import SDGGoalSchemaBase, SDGGoalSchemaFull
from schemas.sdgs.target import SDGTargetSchemaBase, SDGTargetSchemaFull
from settings.settings import SDGsRouterSettings
from utils.logger import logger

# Setup Logging
sdgs_router_settings = SDGsRouterSettings()
logging = logger(sdgs_router_settings.SDGS_ROUTER_LOG_NAME)

# OAuth2 scheme for token authentication
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
    prefix="/sdgs",
    tags=["SDGs"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

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
            detail=f"An error occurred while fetching the SDG goal {sdg_id}: {e}",
        )

@router.get(
    "/",
    response_model=List[SDGGoalSchemaFull],
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

        # Base query for SDG goals
        goals = db.query(SDGGoal).all()

        # Map the paginated items to Pydantic models
        return [SDGGoalSchemaFull.model_validate(goal) for goal in goals]


    except Exception as e:
        logging.error(f"Error fetching SDG goals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching SDG goals: {e}",
        )

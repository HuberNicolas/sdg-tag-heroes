from collections import defaultdict
from typing import List, Optional, Dict, Tuple, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload

from api.app.security import Security
from api.app.routes.authentication import verify_token
from db.mariadb_connector import engine as mariadb_engine

from models.sdg.sdg_target import SDGTarget
from models.sdg.sdg_goal import SDGGoal
from schemas.sdg_goal import SDGGoalSchemaFull, SDGGoalSchemaBase

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

# Endpoint to get a single SDG goal by its ID with optional inclusion of targets
@router.get("/{sdg_id}", description="Get a single SDG goal by ID with optional inclusion of targets")
async def get_sdg(
    sdg_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    include_targets: Optional[bool] = Query(True, description="Whether to include SDG targets")
) -> Union[SDGGoalSchemaBase, SDGGoalSchemaFull]:
    # Verify the token before proceeding
    user = verify_token(token)
    logging.info(f"Fetching SDG goal with ID: {sdg_id}")

    # Base query for fetching the SDG goal
    if include_targets:
        query = db.query(SDGGoal).options(joinedload(SDGGoal.sdg_targets))  # Include targets
    else:
        query = db.query(SDGGoal)  # Exclude targets

    sdg_goal = query.filter(SDGGoal.id == sdg_id).first()

    if not sdg_goal:
        logging.warning(f"No SDG goal found with ID: {sdg_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SDG goal not found")

    logging.info(f"Returning SDG goal with ID: {sdg_id}")

    # Return the appropriate schema based on the include_targets flag
    if include_targets:
        return SDGGoalSchemaFull.from_orm(sdg_goal)
    else:
        return SDGGoalSchemaBase.from_orm(sdg_goal)

# Endpoint to get all SDG goals with optional inclusion of targets
@router.get("/", description="Get all SDG goals with optional inclusion of targets")
async def get_sdgs(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    include_targets: Optional[bool] = Query(True, description="Whether to include SDG targets")
) -> Union[List[SDGGoalSchemaBase], List[SDGGoalSchemaFull]]:
    # Verify the token before proceeding
    user = verify_token(token)
    logging.info("Fetching all SDG goals")

    # Base query for SDG goals
    if include_targets:
        query = db.query(SDGGoal).options(joinedload(SDGGoal.sdg_targets))  # Include targets
        sdg_goals = query.order_by(SDGGoal.index).all()
        return [SDGGoalSchemaFull.from_orm(goal) for goal in sdg_goals]
    else:
        query = db.query(SDGGoal)  # Exclude targets
        sdg_goals = query.order_by(SDGGoal.index).all()
        return [SDGGoalSchemaBase.from_orm(goal) for goal in sdg_goals]







from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from db.mariadb_connector import engine as mariadb_engine
from models import User
from enums.enums import UserRole
from api.app.routes.authentication import verify_token
from api.app.security import Security
from requests_models.user import UserIdsRequest
from schemas.users.user import UserSchemaFull
from settings.settings import UsersRouterSettings
from utils.logger import logger

# Setup Logging
users_router_settings = UsersRouterSettings()
logging = logger(users_router_settings.USERS_ROUTER_LOG_NAME)

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

# Create the API router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

@router.get("/", response_model=List[UserSchemaFull], description="Retrieve users filtered by role")
async def get_users_by_role(
    role: Optional[UserRole] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve users filtered by role. If no role is specified, returns all users.
    """
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Fetch all users
        users = db.query(User).all()
        print(role)

        # Filter users by role
        if role and role != UserRole.USER:
            # Filter based on the 'roles' property
            filtered_users = [u for u in users if role.value in [r.value for r in u.roles]]
        else:
            # Return all Users when UserRole.USER
            filtered_users = users

        return [UserSchemaFull.model_validate(user) for user in filtered_users]


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching users: {e}",
        )

@router.get("/{user_id}", response_model=UserSchemaFull, description="Retrieve a specific user by ID")
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        user = verify_token(token, db)  # Ensure user is authenticated

        # Query for the user by ID
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return UserSchemaFull.model_validate(user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the user",
        )


@router.post(
    "/",
    response_model=List[UserSchemaFull],
    description="Get a list of users by IDs"
)
async def get_publications_by_ids(
    request: UserIdsRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> List[UserSchemaFull]:
    user = verify_token(token, db)  # Ensure user is authenticated

    if request.user_ids:
        user_ids = request.user_ids  # Access the list of IDs

        users = db.query(User).filter(User.user_id.in_(user_ids)).all()

        return [UserSchemaFull.model_validate(user) for user in users]

    else:
        users = db.query(User).all()
        return [UserSchemaFull.model_validate(user) for user in users]

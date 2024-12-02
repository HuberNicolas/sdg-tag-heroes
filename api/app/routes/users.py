from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate

from db.mariadb_connector import engine as mariadb_engine
from models import User
from api.app.routes.authentication import verify_token
from api.app.security import Security
from schemas.users.user import UserSchemaFull, UserRoleEnum

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


@router.get("/", response_model=Page[UserSchemaFull], description="Retrieve users filtered by role")
async def get_users(
    role: Optional[UserRoleEnum] = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve users filtered by role. If no role is specified, returns all users.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        query = db.query(User)

        if role:
            query = query.filter(User._roles.contains(f'"{role}"'))

        return sqlalchemy_paginate(query)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching users",
        )

@router.get("/{user_id}", response_model=UserSchemaFull, description="Retrieve a specific user by ID")
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieve a specific user by their ID.
    """
    try:
        user = verify_token(token)  # Ensure user is authenticated

        # Query for the user by ID
        user_instance = db.query(User).filter(User.user_id == user_id).first()

        if not user_instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        return user_instance

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the user",
        )

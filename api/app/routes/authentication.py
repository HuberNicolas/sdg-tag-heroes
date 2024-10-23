from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from pydantic import BaseModel

from typing import Optional
from pydantic import BaseModel
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
from datetime import timedelta, datetime, timezone

from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from settings.settings import AuthenticationRouterSettings

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


security = Security()
authentication_router_settings = AuthenticationRouterSettings()

SECRET_KEY = security.SECRET_KEY
ALGORITHM = security.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = security.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context (bcrypt)
pwd_context = security.pwd_context

# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme


# Setup Logging
from utils.logger import logger
logging = logger(authentication_router_settings.AUTHENTICATION_ROUTER_LOG_NAME)

# Initialize the router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

# Define the TokenData model to store extracted token claims
class TokenData(BaseModel):
    email: str
    role: str


# Function to verify JWT tokens and extract claims using PyJWT
def verify_token(token: str):
    try:
        # Decode the token using PyJWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        role: str = payload.get("role")


        logging.info(f"Decoded payload: {payload}")

        if email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing claims",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(email=email, role=role)

    # Handle various exceptions from PyJWT

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to decode token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    return {"email": user.email, "role": user.role}

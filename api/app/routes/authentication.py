from datetime import timedelta, datetime, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
from sqlalchemy.orm import Session, sessionmaker

from api.app.security import Security
from db.mariadb_connector import engine as mariadb_engine
from models.users.user import User
from schemas import UserDataSchemaFull, TokenDataSchemaFull, LoginSchemaFull
from requests_models import LoginRequest
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

# Secrets and Security
security = Security()
SECRET_KEY = security.SECRET_KEY
ALGORITHM = security.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = security.ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing context (bcrypt)
pwd_context = security.pwd_context

# OAuth2 scheme for token authentication
oauth2_scheme = security.oauth2_scheme


# Setup Logging
authentication_router_settings = AuthenticationRouterSettings()
from utils.logger import logger
logging = logger(authentication_router_settings.AUTHENTICATION_ROUTER_LOG_NAME)

# Initialize the router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)


# Function to verify JWT tokens and extract claims using PyJWT
def verify_token(token: str, db: Session):
    try:
        # Decode the token using PyJWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        roles: list = payload.get("roles")

        if email is None or roles is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing claims",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Query the database for the user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logging.info(f"Verify token function: User {user} is authenticated")

        return TokenDataSchemaFull(user_id=user.user_id, email=user.email, roles=roles)

    # Handle various exceptions from PyJWT

    except InvalidTokenError:
        logging.error(f"Invalid token: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except ExpiredSignatureError:
        logging.error(f"Expired token: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except DecodeError:
        logging.error(f"Decode Error: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to decode token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
        Protected endpoint that requires JWT authentication.

        Parameters:
            token: The JWT provided in the Authorization header.
            db: The database session.

        Returns:
            Information about the authenticated user.
        """
    user_token = verify_token(token, db)
    return UserDataSchemaFull(user_id=user_token.user_id, email=user_token.email, roles=user_token.roles)

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login route for user authentication.

    Parameters:
        request: A JSON object containing 'email' and 'password'.
        db: The database session.

    Returns:
        A JWT token upon successful authentication.
    """

    # Query the user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        logging.error(f"User not found: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify the provided password against the stored hash
    if not pwd_context.verify(request.password, user.hashed_password):
        logging.error(f"Invalid password: {request.password}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Deserialize roles from the user
    user_roles = [role.value for role in user.roles]

    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {
            "sub": user.email,
            "email": user.email,
            "roles": user_roles,
            "exp": datetime.now(tz=timezone.utc) + access_token_expires,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    logging.info(f"User {request.email} logged in successfully.")

    return LoginSchemaFull(access_token=access_token, token_type="bearer")

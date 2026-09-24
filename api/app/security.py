from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from settings.settings import AuthenticationRouterSettings
from utils.env_loader import get_env_variable, load_env

authentication_router_settings = AuthenticationRouterSettings()


class Security:
    # Load the Backend environment variables
    load_env("backend.env")

    SECRET_KEY = get_env_variable("SECRET_KEY")
    ALGORITHM = get_env_variable("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES"))

    # Password hashing context (bcrypt)
    pwd_context = CryptContext(
        schemes=[authentication_router_settings.CRYPT_CONTEXT_SCHEMA],
        deprecated=authentication_router_settings.CRYPT_CONTEXT_DEPRECATED,
    )

    # OAuth2 scheme for token authentication
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=authentication_router_settings.TOKEN_URL)

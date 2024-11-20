from sqlalchemy import Column, String, Boolean, Enum, Integer
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext
from enum import Enum as PyEnum
from models.base import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Define user roles as an Enum
class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"
    LABELER = "labeler"
    EXPERT = "expert"


class User(Base):
    """
    Base user model for FastAPI with SQLAlchemy.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.USER)

    def verify_password(self, password: str) -> bool:
        """
        Verify the provided password against the hashed password.
        """
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        """
        Hash and set the user's password.
        """
        self.hashed_password = pwd_context.hash(password)

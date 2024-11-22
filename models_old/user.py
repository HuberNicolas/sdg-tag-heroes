from datetime import datetime

from sqlalchemy import Column, String, Boolean, Enum, Integer, DateTime, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import declarative_base, relationship
from passlib.context import CryptContext
from enum import Enum as PyEnum
from models.base import Base

from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

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

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Roles array
    roles = Column(JSON, default=lambda: [UserRole.USER], nullable=False)

    # Optional one-to-one relationships
    labeler_id = Column(Integer, ForeignKey("labelers.labeler_id"), nullable=True, unique=True)
    expert_id = Column(Integer, ForeignKey("experts.expert_id"), nullable=True, unique=True)

    labeler = relationship(
        "Labeler",
        back_populates="user",
        uselist=False,
    )
    expert = relationship(
        "Expert",
        back_populates="user",
        uselist=False,
    )

    # Relationship to SDGUserLabel
    sdg_user_labels = relationship("SDGUserLabel", back_populates="user", cascade="all, delete-orphan")


    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        onupdate=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )

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

import json
from datetime import datetime
from typing import List

from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from passlib.context import CryptContext

from models.associations import user_group_association
from models.base import Base
from enums.enums import UserRole
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    Base user model for FastAPI with SQLAlchemy using Mapped.
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nickname: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Directly mapped column for roles as JSON
    _roles: Mapped[str] = mapped_column("roles", JSON, default=lambda: json.dumps([UserRole.USER.value]),
                                        nullable=False)

    def __init__(self, email: str, nickname: str = None, hashed_password: str = None, roles: List[UserRole] = None, **kwargs):
        """
        Custom initializer to handle `roles` and other parameters.
        """
        self.nickname = nickname
        self.email = email
        self.is_active = kwargs.get('is_active', True)
        self._roles = json.dumps([role.value for role in (roles or [UserRole.USER])])
        if hashed_password:
            self.set_password(hashed_password)

    @hybrid_property
    def roles(self) -> List[UserRole]:
        """Deserialize roles from JSON to List[UserRole]."""
        if isinstance(self._roles, str):
            # Deserialize JSON string
            return [UserRole(role) for role in json.loads(self._roles)]
        elif isinstance(self._roles, list):
            # Handle direct list (e.g., migrations or in-memory objects)
            return [UserRole(role) for role in self._roles]
        else:
            raise TypeError(f"Unexpected type for _roles: {type(self._roles)}")

    @roles.setter
    def roles(self, roles: List[UserRole]):
        """Serialize roles from List[UserRole] to JSON."""
        self._roles = json.dumps([role.value for role in roles])

    admin: Mapped["Admin"] = relationship("Admin", back_populates="user", uselist=False)
    expert: Mapped["Expert"] = relationship("Expert", back_populates="user", uselist=False)
    labeler: Mapped["Labeler"] = relationship("Labeler", back_populates="user", uselist=False)

    # Relationship to Annotations
    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation", back_populates="user", cascade="all, delete-orphan"
    )

    # Relationship to SDGUserLabels
    sdg_user_labels: Mapped[list["SDGUserLabel"]] = relationship(
        "SDGUserLabel", back_populates="user", cascade="all, delete-orphan"
    )

    # Relationship to Votes
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="user", cascade="all, delete-orphan"
    )

    # One-to-Many relationship with SDGLabelDecision (as an Expert)
    sdg_label_decisions: Mapped[list["SDGLabelDecision"]] = relationship(
        "SDGLabelDecision", back_populates="expert"
    )

    # Many-to-Many relationship with Group
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=user_group_association,
        back_populates="members"
    )

    # One-to-One relationship with Inventory
    inventory: Mapped["Inventory"] = relationship(
        "Inventory",
        back_populates="user",
        uselist=False,  # Ensure one-to-one
        cascade="all, delete-orphan"
    )

    # One-to-One relationship with SDGCoinWallet
    sdg_coin_wallet: Mapped["SDGCoinWallet"] = relationship(
        "SDGCoinWallet",
        back_populates="user",
        uselist=False,  # Ensure one-to-one
        cascade="all, delete-orphan"
    )

    # One-to-One relationship with SDGXPBank
    sdg_xp_bank: Mapped["SDGXPBank"] = relationship(
        "SDGXPBank",
        back_populates="user",
        uselist=False,  # Ensure one-to-one
        cascade="all, delete-orphan"
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
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

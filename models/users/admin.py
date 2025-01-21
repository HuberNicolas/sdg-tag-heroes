from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Admin(Base):
    """
    Admin role, extending the User.
    Represents a one-to-one relationship where an Admin is always linked to exactly one User.
    """
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)

    # Relationship to the User
    user: Mapped["User"] = relationship("User", back_populates="admin", uselist=False)

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

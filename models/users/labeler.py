from datetime import datetime

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Labeler(Base):
    """
    Labeler role, extending the User.
    Represents a one-to-one relationship where an Labeler is always linked to exactly one User.
    """
    __tablename__ = "labelers"

    labeler_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)

    # Relationship to the User
    user: Mapped["User"] = relationship("User", back_populates="labeler", uselist=False)

    labeler_score: Mapped[float] = mapped_column(nullable=False)

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

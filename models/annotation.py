from sqlalchemy import ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from settings.settings import TimeZoneSettings
from models import Base

time_zone_settings = TimeZoneSettings()


class Annotation(Base):
    """
    Annotation model representing content created by a user.
    """
    __tablename__ = "annotations"

    annotation_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key linking to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Foreign key linking to the SDGUserLabel
    sdg_user_label_id: Mapped[int] = mapped_column(ForeignKey("sdg_user_labels.label_id"), nullable=False)

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="annotations")

    # Relationship to SDGUserLabel
    sdg_user_label: Mapped["SDGUserLabel"] = relationship("SDGUserLabel", back_populates="annotations")


    labeler_score: Mapped[float] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(Text(), nullable=False)

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

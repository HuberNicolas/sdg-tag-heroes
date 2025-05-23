from datetime import datetime

from sqlalchemy import Enum, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.enums import VoteType
from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

class Vote(Base):
    """
    Represents a vote on an SDGUserLabel or Annotation by a User. The vote can be positive, neutral, or negative.
    """
    __tablename__ = "votes"

    vote_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key linking to the User who created the vote
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Foreign key linking to the SDGUserLabel being voted on
    sdg_user_label_id: Mapped[int] = mapped_column(ForeignKey("sdg_user_labels.label_id"), nullable=True)

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="votes")

    # Foreign key linking to the Annotation being voted on
    annotation_id: Mapped[int] = mapped_column(ForeignKey("annotations.annotation_id"), nullable=True)

    # Relationship to SDGUserLabel
    sdg_user_label: Mapped["SDGUserLabel"] = relationship("SDGUserLabel", back_populates="votes")

    # Relationship to Annotation
    annotation: Mapped["Annotation"] = relationship("Annotation", back_populates="votes")

    vote_type: Mapped[VoteType] = mapped_column(Enum(VoteType), default=VoteType.NEUTRAL, nullable=False)

    score : Mapped[float] = mapped_column(default=0, nullable=False)


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

    __table_args__ = (
        CheckConstraint(
            "(sdg_user_label_id IS NOT NULL AND annotation_id IS NULL) OR "
            "(sdg_user_label_id IS NULL AND annotation_id IS NOT NULL)",
            name="check_one_target_not_both"
        ),
    )

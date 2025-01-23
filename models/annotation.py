from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Annotation(Base):
    """
    Annotation model representing content created by a user.
    """
    __tablename__ = "annotations"

    annotation_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key linking to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Optional foreign key linking to SDGUserLabel
    sdg_user_label_id: Mapped[int | None] = mapped_column(ForeignKey("sdg_user_labels.label_id"), nullable=True)

    # Optional foreign key linking to SDGLabelDecision
    decision_id: Mapped[int | None] = mapped_column(ForeignKey("sdg_label_decisions.decision_id"), nullable=True)

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="annotations")

    # Relationship to SDGUserLabel (optional)
    sdg_user_label: Mapped["SDGUserLabel"] = relationship("SDGUserLabel", back_populates="annotations",
                                                          foreign_keys=[sdg_user_label_id])
    # Relationship to SDGLabelDecision (optional)
    decision: Mapped["SDGLabelDecision"] = relationship("SDGLabelDecision", back_populates="annotations",
                                                        foreign_keys=[decision_id])
    # Relationship to Votes
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="annotation", cascade="all, delete-orphan"
    )

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

    # Ensure only one of `sdg_user_label_id` or `decision_id` is set
    __table_args__ = (
        CheckConstraint(
            "((sdg_user_label_id IS NOT NULL AND decision_id IS NULL) OR "
            "(sdg_user_label_id IS NULL AND decision_id IS NOT NULL))",
            name="check_annotation_target",
        ),
    )

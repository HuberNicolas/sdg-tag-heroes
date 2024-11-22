from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.associations import sdg_label_decision_user_label_association
class SDGUserLabel(Base):
    """
    Represents a user-defined label in the SDG system.
    """
    __tablename__ = "sdg_user_labels"

    label_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key linking to the User who authored the label
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationship to User
    user: Mapped["User"] = relationship("User", back_populates="sdg_user_labels")

    # Relationship to Annotations
    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation", back_populates="sdg_user_label", cascade="all, delete-orphan"
    )

    # Relationship to Votes
    votes: Mapped[list["Vote"]] = relationship(
        "Vote", back_populates="sdg_user_label", cascade="all, delete-orphan"
    )

    # Many-to-Many relationship with SDGLabelDecision
    label_decisions: Mapped[list["SDGLabelDecision"]] = relationship(
        "SDGLabelDecision",
        secondary=sdg_label_decision_user_label_association,
        back_populates="user_labels"
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)

    labeled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
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


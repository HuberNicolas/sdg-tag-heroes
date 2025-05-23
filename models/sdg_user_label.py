from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Integer, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models import Base
from models.associations import sdg_label_decision_user_label_association
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


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

    proposed_label: Mapped[int] = mapped_column(Integer, nullable=True)
    voted_label: Mapped[int] = mapped_column(Integer, nullable=False)
    abstract_section: Mapped[str] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    # ForeignKey
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"), nullable=False)

    # Relationship to Publication
    publication: Mapped["Publication"] = relationship("Publication", back_populates="user_labels")


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

    # 18 -> Null Class
    # 0 -> Not defined yet, but it could be "not defined yet"
    # 1 ... 17 -> SDG
    __table_args__ = (
        CheckConstraint("(proposed_label >= -1 AND proposed_label <= 18)", name="check_proposed_label_range"),
        CheckConstraint("(voted_label >= -1 AND voted_label <= 18)", name="check_voted_label_range"),
    )

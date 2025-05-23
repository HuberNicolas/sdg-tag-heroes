from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums.enums import DecisionType, ScenarioType
from models import Base
from models.associations import sdg_label_decision_user_label_association
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class SDGLabelDecision(Base):
    """
    Represents a decision related to one or more SDGUserLabels.
    """
    __tablename__ = "sdg_label_decisions"

    decision_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    suggested_label: Mapped[int] = mapped_column(Integer, nullable=False)
    decided_label: Mapped[int] = mapped_column(Integer, default=0, nullable=False) # 0 not decided, 18 zero class
    decision_type: Mapped[DecisionType] = mapped_column(Enum(DecisionType), default=DecisionType.CONSENSUS_MAJORITY, nullable=False)
    scenario_type: Mapped[ScenarioType] = mapped_column(Enum(ScenarioType), default=ScenarioType.NOT_ENOUGH_VOTES, nullable=False)

    # Many-to-Many relationship with SDGUserLabel
    user_labels: Mapped[list["SDGUserLabel"]] = relationship(
        "SDGUserLabel",
        secondary=sdg_label_decision_user_label_association,
        back_populates="label_decisions"
    )


    # Optional One-to-Many relationship with Expert
    expert_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    expert: Mapped["User"] = relationship("User", back_populates="sdg_label_decisions")

    # Foreign key linking to SDGLabelHistory
    history_id: Mapped[int] = mapped_column(ForeignKey("sdg_label_histories.history_id"), nullable=True)
    # Relationship back to SDGLabelHistory
    history: Mapped["SDGLabelHistory"] = relationship("SDGLabelHistory", back_populates="decisions")

    # Relationship to Annotations
    annotations: Mapped[list["Annotation"]] = relationship(
        "Annotation",
        back_populates="decision",
        cascade="all, delete-orphan",
    )


    comment: Mapped[str] = mapped_column(Text(), nullable=True)

    # Add publication_id ForeignKey
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"), nullable=False)

    # Relationship to Publication
    publication: Mapped["Publication"] = relationship("Publication", back_populates="label_decisions")

    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=True,
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

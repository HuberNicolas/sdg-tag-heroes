from datetime import datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship

from models.base import Base

from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class Expert(Base):
    """
    Expert role, extending the Labeler.
    """
    __tablename__ = "experts"

    expert_id = Column(Integer, primary_key=True, autoincrement=True)  # Autonomous ID
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)

    user = relationship(
        "User",
        back_populates="expert",
        uselist=False,
        foreign_keys=[user_id],
        remote_side="User.user_id",  # Specify the "parent" side
    )
    expert_score = Column(Float, nullable=True)


    sdg_label_decisions = relationship("SDGLabelDecision", back_populates="expert")

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

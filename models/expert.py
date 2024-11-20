from datetime import datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, DateTime
from .labeler import Labeler

from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class Expert(Labeler):
    """
    Expert role, extending the Labeler.
    """
    __tablename__ = "experts"

    expert_id = Column(Integer, ForeignKey("labelers.labeler_id"), primary_key=True)
    expert_score = Column(Float, nullable=True)

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

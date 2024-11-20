from datetime import datetime
from sqlalchemy import Column, Float, Integer, ForeignKey, DateTime
from .user import User


from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class Labeler(User):
    """
    Labeler role, extending the User.
    """
    __tablename__ = "labelers"

    labeler_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    labeling_score = Column(Float, nullable=True)

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

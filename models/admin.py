from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime
from .user import User

from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class Admin(User):
    """
    Admin role, extending the User.
    """
    __tablename__ = "admins"

    admin_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

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

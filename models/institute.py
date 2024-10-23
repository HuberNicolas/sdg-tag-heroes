from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base


class Institute(Base):
    __tablename__ = "institutes"
    institute_id = Column(Integer, primary_key=True)
    institute_setSpec = Column(String(255), nullable=False, unique=True)
    institute_name = Column(String(255), nullable=False, unique=False)
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

    def __repr__(self):
        return (
            f"<Institute(institute_id={self.institute_id}, "
            f"institute_setSpec={self.institute_setSpec}, "
            f"institute_name={self.institute_name}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

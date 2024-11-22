from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base


class Faculty(Base):
    __tablename__ = "faculties"
    faculty_id = Column(Integer, primary_key=True)
    faculty_setSpec = Column(String(255), nullable=False, unique=True)
    faculty_name = Column(String(255), nullable=False, unique=False)
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
            f"<Faculty(faculty_id={self.faculty_id}, "
            f"faculty_setSpec={self.faculty_setSpec}, "
            f"faculty_name={self.faculty_name}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


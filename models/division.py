from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base

# setName Communities & Collections = 04 Faculty of Medicine: University Hospital Zurich: Division of Psychosocial Medicine (former)
# setSpec	7375626A656374733D3130313730:3130313938:3130303539
# Be aware: There can be up to 5 elements


class Division(Base):
    __tablename__ = "divisions"
    division_id = Column(Integer, primary_key=True)
    division_setSpec = Column(String(255), nullable=False, unique=True)
    division_name = Column(String(255), nullable=False, unique=False)
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
            f"<Division(division_id={self.division_id}, "
            f"division_setSpec={self.division_setSpec}, "
            f"division_name={self.division_name}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


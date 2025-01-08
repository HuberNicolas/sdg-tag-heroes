from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class Institute(Base):
    __tablename__ = "institutes"

    institute_id: Mapped[int] = mapped_column(primary_key=True)
    institute_setSpec: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    institute_name: Mapped[str] = mapped_column(String(255), nullable=False)
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

    def __repr__(self):
        return (
            f"<Institute(institute_id={self.institute_id}, "
            f"institute_setSpec={self.institute_setSpec}, "
            f"institute_name={self.institute_name}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

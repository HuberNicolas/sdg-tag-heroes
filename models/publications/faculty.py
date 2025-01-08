from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class Faculty(Base):
    __tablename__ = "faculties"

    faculty_id: Mapped[int] = mapped_column(primary_key=True)
    faculty_setSpec: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    faculty_name: Mapped[str] = mapped_column(String(255), nullable=False)
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
            f"<Faculty(faculty_id={self.faculty_id}, "
            f"faculty_setSpec={self.faculty_setSpec}, "
            f"faculty_name={self.faculty_name}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

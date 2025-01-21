from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Division(Base):
    # setName Communities & Collections = 04 Faculty of Medicine: University Hospital Zurich: Division of Psychosocial Medicine (former)
    # setSpec	7375626A656374733D3130313730:3130313938:3130303539
    # Be aware: There can be up to 5 elements


    __tablename__ = "divisions"

    division_id: Mapped[int] = mapped_column(primary_key=True)
    division_setSpec: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    division_name: Mapped[str] = mapped_column(String(255), nullable=False)
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
            f"<Division(division_id={self.division_id}, "
            f"division_setSpec={self.division_setSpec}, "
            f"division_name={self.division_name}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

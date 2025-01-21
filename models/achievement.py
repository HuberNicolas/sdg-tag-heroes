from sqlalchemy import String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Achievement(Base):
    """
    Achievement model for badges or achievements.
    An achievement can belong to multiple inventories (users).
    """
    __tablename__ = "achievements"

    achievement_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    # Updated Many-to-Many relationship with Inventories through association model
    inventory_achievements: Mapped[list["InventoryAchievementAssociation"]] = relationship(
        "InventoryAchievementAssociation",
        back_populates="achievement",
        cascade="all, delete-orphan"
    )

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

from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class InventoryAchievementAssociation(Base):
    """
    Association model for the many-to-many relationship between Inventory and Achievement.
    Adds additional metadata like a comment and timestamp.
    """
    __tablename__ = "inventory_achievement_association"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventories.inventory_id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.achievement_id"), nullable=False)

    # Additional fields
    comment: Mapped[str] = mapped_column(String(255), nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships to Inventory and Achievement
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="inventory_achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="inventory_achievements")


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

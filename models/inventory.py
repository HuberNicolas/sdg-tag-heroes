
from sqlalchemy import Table, ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Inventory(Base):
    """
    Inventory model for each user.
    Each user has exactly one inventory.
    """
    __tablename__ = "inventories"

    inventory_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), unique=True, nullable=False)

    # One-to-One relationship with User
    user: Mapped["User"] = relationship("User", back_populates="inventory")

    # Updated Many-to-Many relationship with Achievements through association model
    inventory_achievements: Mapped[list["InventoryAchievementAssociation"]] = relationship(
        "InventoryAchievementAssociation",
        back_populates="inventory",
        cascade="all, delete-orphan"
    )

    @property
    def achievements(self):
        """Convenience property to get achievements directly."""
        return [assoc.achievement for assoc in self.inventory_achievements]

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

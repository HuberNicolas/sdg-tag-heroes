from datetime import datetime
from typing import Tuple

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums import SDGType
from models.base import Base
from settings.settings import TimeZoneSettings, MariaDBSettings

time_zone_settings = TimeZoneSettings()
mariadb_settings = MariaDBSettings()

class SDGRank(Base):
    """
    Tracks the gamification rank for each SDG goal (1-17) with corresponding XP thresholds.
    """
    __tablename__ = "sdg_ranks"

    rank_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sdg_goal_id: Mapped[int] = mapped_column(Integer, nullable=False)  # SDG Goal ID (1-17)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)  # Rank tier (0, 1, 2, 3)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Rank name
    description: Mapped[str] = mapped_column(String(255), nullable=True)  # Rank description
    xp_required: Mapped[Float] = mapped_column(Float, nullable=False)  # XP required for this rank

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
        return f"<SDGRank(rank_id={self.rank_id}, sdg_goal_id={self.sdg_goal_id}, tier={self.tier}, name={self.name}, xp_required={self.xp_required})>"


from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class SDGXPBank(Base):
    """
    Model to track user achievements and accumulated XP.
    """
    __tablename__ = "sdg_xp_banks"

    sdg_xp_bank_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, unique=True)
    total_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # SDG-specific XP values
    sdg1_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg2_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg3_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg4_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg5_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg6_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg7_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg8_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg9_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg10_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg11_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg12_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg13_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg14_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg15_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg16_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sdg17_xp: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Define relationship with User
    user: Mapped["User"] = relationship("User", back_populates="sdg_xp_bank")

    # Relationship to track changes over time
    histories: Mapped[list["SDGXPBankHistory"]] = relationship(
        "SDGXPBankHistory",
        back_populates="xp_bank",
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

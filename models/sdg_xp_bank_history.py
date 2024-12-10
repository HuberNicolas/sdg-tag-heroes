from sqlalchemy import ForeignKey, Float, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime
from sqlalchemy import Enum
from settings.enums import SDGEnum



from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class SDGXPBankHistory(Base):
    """
    Tracks incremental changes in the SDGXPBank over time.
    """
    __tablename__ = "sdg_xp_bank_histories"

    history_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    xp_bank_id: Mapped[int] = mapped_column(ForeignKey("sdg_xp_banks.sdg_xp_bank_id"), nullable=False)
    sdg: Mapped[SDGEnum] = mapped_column(Enum(SDGEnum), nullable=False)  # Enum to specify SDG
    increment: Mapped[float] = mapped_column(Float, nullable=False)  # Incremental change in XP (+/-)
    reason: Mapped[str] = mapped_column(String(255), nullable=True)  # Optional reason for the change
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(time_zone_settings.ZURICH_TZ), nullable=False)

    # Relationship with SDGXPBank
    xp_bank: Mapped["SDGXPBank"] = relationship("SDGXPBank", back_populates="histories")

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

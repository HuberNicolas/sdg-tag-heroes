from sqlalchemy import ForeignKey, Float, DateTime, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base
from datetime import datetime

from settings.settings import TimeZoneSettings
time_zone_settings = TimeZoneSettings()

class SDGCoinWalletHistory(Base):
    """
    Tracks incremental changes in the SDGCoinWallet over time.
    """
    __tablename__ = "sdg_coin_wallet_histories"

    history_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    wallet_id: Mapped[int] = mapped_column(ForeignKey("sdg_coin_wallets.sdg_coin_wallet_id"), nullable=False)
    increment: Mapped[float] = mapped_column(Float, nullable=False)  # Incremental change in coins (+/-)
    reason: Mapped[str] = mapped_column(Text, nullable=True)  # Optional reason for the change
    is_shown: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(time_zone_settings.ZURICH_TZ), nullable=False)

    # Relationship with SDGCoinWallet
    wallet: Mapped["SDGCoinWallet"] = relationship("SDGCoinWallet", back_populates="histories")

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

    def __repr__(self) -> str:
        return (
            f"<SDGCoinWalletHistory("
            f"history_id={self.history_id}, "
            f"wallet_id={self.wallet_id}, "
            f"increment={self.increment}, "
            f"reason={self.reason!r}, "
            f"is_shown={self.is_shown}, "
            f"timestamp={self.timestamp}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}"
            f")>"
        )


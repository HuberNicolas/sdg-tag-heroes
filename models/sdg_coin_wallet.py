from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class SDGCoinWallet(Base):
    """
    CoinWallet model to store SDG coins for each user.
    """
    __tablename__ = "sdg_coin_wallets"

    sdg_coin_wallet_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, unique=True)
    total_coins: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Define relationship with User
    user: Mapped["User"] = relationship("User", back_populates="sdg_coin_wallet")

    # Relationship to track changes over time
    histories: Mapped[list["SDGCoinWalletHistory"]] = relationship(
        "SDGCoinWalletHistory",
        back_populates="wallet",
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

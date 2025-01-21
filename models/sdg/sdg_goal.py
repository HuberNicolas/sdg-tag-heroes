from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings


class SDGGoal(Base):
    __tablename__ = "sdg_goals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    index: Mapped[int] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)  # Hex code color
    icon: Mapped[str | None] = mapped_column(LONGTEXT)  # Base64 encoded SVG as LONGTEXT

    # Relationship with SDGTarget
    sdg_targets: Mapped[list["SDGTarget"]] = relationship("SDGTarget", back_populates="sdg_goal")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        onupdate=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        nullable=False,
    )

    def __repr__(self):
        return f"<SDGGoal(index={self.index}, name={self.name}, color={self.color})>"

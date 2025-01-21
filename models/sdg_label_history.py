from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class SDGLabelHistory(Base):
    """
    Represents a historical record of SDG label evaluations.
    """
    __tablename__ = "sdg_label_histories"

    history_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # One-to-Many relationship with SDGLabelDecision
    decisions: Mapped[list["SDGLabelDecision"]] = relationship(
        "SDGLabelDecision", back_populates="history", cascade="all, delete-orphan"
    )

    # One-to-One relationship with SDGLabelSummary
    label_summary: Mapped["SDGLabelSummary"] = relationship(
        "SDGLabelSummary", back_populates="history", uselist=False
    )

    active: Mapped[bool] = mapped_column(default=True, nullable=False)

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
            f"<SDGLabelHistory("
            f"history_id={self.history_id}, "
            f"active={self.active}, "
            f"created_at={self.created_at.isoformat() if self.created_at else None}, "
            f"updated_at={self.updated_at.isoformat() if self.updated_at else None}, "
            f"decisions_count={len(self.decisions) if self.decisions else 0}, "
            f"label_summary={'present' if self.label_summary else 'absent'}"
            f")>"
        )

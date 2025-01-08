from sqlalchemy import ForeignKey, String, DateTime, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class SDGLabelSummary(Base):
    """
    Represents a single SDG label summary tied to exactly one history.
    """
    __tablename__ = "sdg_label_summaries"

    sdg_label_summary_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ForeignKey to Publication
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"), unique=True, nullable=False)
    publication: Mapped["Publication"] = relationship("Publication", back_populates="sdg_label_summary")

    # One-to-One relationship with SDGLabelHistory
    history_id: Mapped[int] = mapped_column(ForeignKey("sdg_label_histories.history_id"), unique=True, nullable=False)
    history: Mapped["SDGLabelHistory"] = relationship("SDGLabelHistory", back_populates="label_summary")

    # Columns for each SDG goal label
    sdg1: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg1 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg2: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg2 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg3: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg3 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg4: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg4 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg5: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg5 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg6: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg6 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg7: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg7 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg8: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg8 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg9: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg9 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg10: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg10 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg11: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg11 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg12: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg12 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg13: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg13 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg14: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg14 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg15: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg15 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg16: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg16 IN (-1, 0, 1)'), nullable=False, default=0)
    sdg17: Mapped[int] = mapped_column(Integer, CheckConstraint('sdg17 IN (-1, 0, 1)'), nullable=False, default=0)

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
        active_sdgs = [
            f"SDG{i}" for i in range(1, 18)
            if getattr(self, f"sdg{i}") == 1
        ]
        return (
            f"<SDGLabelSummary("
            f"id={self.sdg_label_summary_id}, "
            f"publication_id={self.publication_id}, "
            f"history_id={self.history_id}, "
            f"active_sdgs={active_sdgs}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}"
            f")>"
        )

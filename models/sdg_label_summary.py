from sqlalchemy import ForeignKey, String, DateTime
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

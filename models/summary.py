from sqlalchemy import Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Summary(Base):
    """
    Represents a concise summary of a publication, with one-to-one mapping.
    """
    __tablename__ = "summaries"

    summary_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    content: Mapped[str | None] = mapped_column(Text)

    publication_id: Mapped[int] = mapped_column(
        ForeignKey("publications.publication_id", ondelete="cascade"),
        unique=True,  # Ensures one-to-one mapping
        nullable=False
    )
    publication: Mapped["Publication"] = relationship(
        "Publication", back_populates="summary"
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

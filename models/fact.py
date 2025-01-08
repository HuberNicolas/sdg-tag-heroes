from sqlalchemy import Enum, ForeignKey, DateTime, CheckConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from models import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Fact(Base):
    """
    Represents an interesting fact based on the content (abstract) and title from a publication.
    """
    __tablename__ = "facts"

    fact_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    content: Mapped[str | None] = mapped_column(Text)

    publication_id: Mapped[int] = mapped_column(
        ForeignKey("publications.publication_id", ondelete="cascade"),
        unique=True,  # Ensures one-to-one mapping
        nullable=False
    )
    publication: Mapped["Publication"] = relationship(
        "Publication", back_populates="fact"
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

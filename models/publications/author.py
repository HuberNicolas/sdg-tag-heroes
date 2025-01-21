from datetime import datetime
from sqlalchemy import String, DateTime, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Author(Base):
    __tablename__ = "authors"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # Full name
    lastname: Mapped[str] = mapped_column(String(255))  # Extracted last name
    surname: Mapped[str] = mapped_column(String(255))  # Extracted surname
    orcid_id: Mapped[str] = mapped_column(String(255), nullable=True)

    # String-based relationship to avoid circular imports
    publications: Mapped[list["Publication"]] = relationship(
        "Publication", secondary="publication_authors", back_populates="authors"
    )

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
        return (
            f"<Author(author_id={self.author_id}, "
            f"name={self.name}, "
            f"lastname={self.lastname}, "
            f"surname={self.surname}, "
            f"orcid_id={self.orcid_id}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )


@event.listens_for(Author, "before_insert")
@event.listens_for(Author, "before_update")
def set_lastname_and_surname(mapper, connection, target):
    if target.name:
        parts = target.name.split(",")

        # Extract the last name
        target.lastname = parts[0].strip() if len(parts) > 0 else None

        # Extract the surname
        target.surname = parts[1].strip() if len(parts) > 1 else None

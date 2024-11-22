from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, event
from sqlalchemy.orm import relationship

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base


class Author(Base):
    __tablename__ = "authors"
    author_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Full name (e.g., "Schwappach, D L B")
    lastname = Column(String(255))  # Extracted last name (e.g., "Schwappach")
    surname = Column(
        String(255)
    )  # Extracted surname (initials or full name after the comma, e.g., "D L B" or "Angelika")
    orcid_id = Column(String(255), nullable=True)  #
    publications = relationship(
        "Publication", secondary="publication_authors", back_populates="authors"
    ) # Use string-based relationship
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(TimeZoneSettings.ZURICH_TZ),
        nullable=False,
    )
    updated_at = Column(
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


# Event listener to automatically set 'lastname' and 'surname' based on 'name'
@event.listens_for(Author, "before_insert")
@event.listens_for(Author, "before_update")
def set_lastname_and_surname(mapper, connection, target):
    """
    Automatically updates the 'lastname' and 'surname' fields before the record is inserted or updated.
    This ensures 'lastname' and 'surname' columns are always in sync with the 'name' column.
    """
    if target.name:
        # Split the name by the comma to extract lastname and surname
        parts = target.name.split(",")

        # Extract the last name (everything before the comma)
        if len(parts) > 0:
            target.lastname = parts[0].strip()
        else:
            target.lastname = None

        # Extract the surname (everything after the comma, typically initials or first name)
        if len(parts) > 1:
            target.surname = parts[1].strip()
        else:
            target.surname = None

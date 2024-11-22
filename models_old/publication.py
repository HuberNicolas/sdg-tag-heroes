import re
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    event,
)
from sqlalchemy.orm import relationship

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base

# Association table for the many-to-many relationship
publication_authors = Table(
    "publication_authors",
    Base.metadata,
    Column(
        "publication_id", ForeignKey("publications.publication_id"), primary_key=True
    ),
    Column("author_id", ForeignKey("authors.author_id"), primary_key=True),
)


class Publication(Base):
    __tablename__ = "publications"
    publication_id = Column(Integer, primary_key=True)
    oai_identifier = Column(String(255), nullable=False, unique=True)
    oai_identifier_num = Column(Integer, nullable=False, unique=True)
    title = Column(Text)
    authors = relationship(
        "Author", secondary="publication_authors", back_populates="publications"
    )
    description = Column(Text)
    publisher = Column(String(255))
    date = Column(String(100))
    year = Column(Integer)
    source = Column(Text)
    language = Column(String(255))
    format = Column(String(200))
    sdg_predictions = relationship(
        "SDGPrediction", back_populates="publication", cascade="all, delete-orphan"
    )
    sdg_label = relationship(
        "SDGLabel", back_populates="publication", uselist=False
    )
    embedded = Column(Boolean, default=False)
    set_spec = Column(Text, default=None)

    faculty_id = Column(Integer, ForeignKey("faculties.faculty_id"), nullable=True)
    faculty = relationship("Faculty")

    institute_id = Column(Integer, ForeignKey("institutes.institute_id"), nullable=True)
    institute = relationship("Institute")

    division_id = Column(Integer, ForeignKey("divisions.division_id"), nullable=True)
    division = relationship("Division")

    # Define the one-to-one relationship with DimRed
    dim_red = relationship("DimRed", back_populates="publication", uselist=False)
    dimreduced = Column(Boolean, default=False)
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
            f"<Publication(publication_id={self.publication_id}, "
            f"title={self.title}, "
            f"oai_identifier={self.oai_identifier}, "
            f"year={self.year}, "
            f"publisher={self.publisher})>"
        )


# Event listener to automatically set the 'year' field based on 'date'
@event.listens_for(Publication, "before_insert")
@event.listens_for(Publication, "before_update")
def set_year_based_on_date(mapper, connection, target):
    """
    Automatically updates the 'year' field before the record is inserted or updated.
    This ensures the 'year' column is always in sync with the 'date' column.
    """
    if target.date:
        # Extract the year using a regular expression (first four digits of the date string)
        match = re.match(r"(\d{4})", target.date)
        if match:
            target.year = int(match.group(1))
        else:
            target.year = None  # Set year to None if no valid year can be extracted

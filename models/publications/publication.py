import re
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    event, Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()

class Publication(Base):
    __tablename__ = "publications"

    publication_id: Mapped[int] = mapped_column(primary_key=True)
    oai_identifier: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    oai_identifier_num: Mapped[int] = mapped_column(nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    publisher: Mapped[str | None] = mapped_column(String(255))
    date: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column()
    source: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(255))
    format: Mapped[str | None] = mapped_column(String(200))
    embedded: Mapped[bool] = mapped_column(default=False)
    set_spec: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    authors: Mapped[list["Author"]] = relationship(
        "Author", secondary="publication_authors", back_populates="publications"
    )

    sdg_label_summary: Mapped["SDGLabelSummary"] = relationship(
        "SDGLabelSummary", back_populates="publication", uselist=False
    )

    sdg_predictions: Mapped[list["SDGPrediction"]] = relationship(
        "SDGPrediction", back_populates="publication", cascade="all, delete-orphan"
    )

    sdg_target_predictions: Mapped[list["SDGTargetPrediction"]] = relationship(
        "SDGTargetPrediction",
        back_populates="publication",
        cascade="all, delete-orphan",
    )

    dimensionality_reductions: Mapped[list["DimensionalityReduction"]] = relationship(
        "DimensionalityReduction", back_populates="publication", cascade="all, delete-orphan"
    )

    clusters: Mapped[list["PublicationCluster"]] = relationship(
        "PublicationCluster", back_populates="publication", cascade="all, delete-orphan"
    )

    fact: Mapped[list["Fact"]] = relationship("Fact", back_populates="publication", uselist=False
    )

    summary: Mapped["Summary"] = relationship("Summary", back_populates="publication", uselist=False
    )

    is_dim_reduced: Mapped[bool] = mapped_column(default=False)

    faculty_id: Mapped[int | None] = mapped_column(ForeignKey("faculties.faculty_id"), nullable=True)
    faculty: Mapped["Faculty | None"] = relationship("Faculty")

    institute_id: Mapped[int | None] = mapped_column(ForeignKey("institutes.institute_id"), nullable=True)
    institute: Mapped["Institute | None"] = relationship("Institute")

    division_id: Mapped[int | None] = mapped_column(ForeignKey("divisions.division_id"), nullable=True)
    division: Mapped["Division | None"] = relationship("Division")

    collection_id: Mapped[int | None] = mapped_column(ForeignKey("collections.collection_id"), nullable=True)
    collection: Mapped["Collection | None"] = relationship("Collection", back_populates="publications")

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
            f"<Publication(publication_id={self.publication_id}, "
            f"title={self.title}, "
            f"oai_identifier={self.oai_identifier}, "
            f"year={self.year}, "
            f"publisher={self.publisher})>, ",
            f"collection_id={self.collection_id}"
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

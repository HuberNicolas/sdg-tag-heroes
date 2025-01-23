import json
from datetime import datetime

from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class Collection(Base):
    __tablename__ = 'collections'

    collection_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)  # Unique topic_id
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str] = mapped_column(String(255), nullable=False)
    representation: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of strings
    aspect1: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of strings
    aspect2: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of strings
    aspect3: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of strings

    # Define the publications relationship
    publications: Mapped[list["Publication"]] = relationship(
        "Publication", back_populates="collection", cascade="all, delete-orphan"
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

    def to_dict(self):
        """
        Converts the SQLAlchemy model instance to a dictionary for Pydantic validation.
        """
        return {
            "collection_id": self.collection_id,
            "topic_id": self.topic_id,
            "count": self.count,
            "name": self.name,
            "short_name": self.short_name,
            # Parse JSON string to list
            "representation": json.loads(self.representation) if self.representation else [],
            "aspect1": json.loads(self.aspect1) if self.aspect1 else [],
            "aspect2": json.loads(self.aspect2) if self.aspect2 else [],
            "aspect3": json.loads(self.aspect3) if self.aspect3 else [],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self):
        return (
            f"<Collection(collection_id={self.collection_id}, "
            f"topic_id={self.topic_id}, "
            f"name={self.name}, "
            f"short_name={self.short_name}, "
            f"count={self.count})>"
        )

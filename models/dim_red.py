from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base


class DimRed(Base):
    __tablename__ = "dim_reds"
    dim_red_id = Column(Integer, primary_key=True)
    publication_id = Column(
        Integer, ForeignKey("publications.publication_id")
    )  # Foreign key to Publication
    umap_x_coord = Column(Float(precision=4), default=0.0, nullable=True, unique=False)
    umap_y_coord = Column(Float(precision=4), default=0.0, nullable=True, unique=False)

    publication = relationship("Publication", back_populates="dim_red")
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
            f"<DimRed(dim_red_id={self.dim_red_id}, "
            f"publication_id={self.publication_id}, "
            f"umap_x_coord={self.umap_x_coord}, "
            f"umap_y_coord={self.umap_y_coord}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class DimensionalityReduction(Base):
    __tablename__ = "dimensionality_reductions"

    dim_red_id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"))

    reduction_technique: Mapped[str | None] = mapped_column(String(255))
    reduction_details: Mapped[str | None] = mapped_column(Text)
    reduction_shorthand: Mapped[str | None] = mapped_column(String(255))

    x_coord: Mapped[float] = mapped_column(Float(precision=4), default=0.0, nullable=True)
    y_coord: Mapped[float] = mapped_column(Float(precision=4), default=0.0, nullable=True)
    z_coord: Mapped[float] = mapped_column(Float(precision=4), default=0.0, nullable=True)

    # New columns for SDG and level
    sdg: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    publication: Mapped["Publication"] = relationship("Publication", back_populates="dimensionality_reductions")

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
            f"<DimensionalityReduction(dim_red_id={self.dim_red_id}, "
            f"publication_id={self.publication_id}, "
            f"reduction_technique={self.reduction_technique}, "
            f"reduction_shorthand={self.reduction_shorthand}, "
            f"x_coord={self.x_coord}, "
            f"y_coord={self.y_coord}, "
            f"z_coord={self.z_coord}, "
            f"sdg={self.sdg}, "
            f"level={self.level}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})>"
        )

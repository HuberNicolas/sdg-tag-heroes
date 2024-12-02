from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from settings.settings import TimeZoneSettings
from models.base import Base

time_zone_settings = TimeZoneSettings()


class SDGPrediction(Base):
    __tablename__ = "sdg_predictions"

    prediction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"), nullable=False)

    # Relationships
    publication: Mapped["Publication"] = relationship("Publication", back_populates="sdg_predictions")

    prediction_model: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Columns for each SDG goal prediction (values from 0 to 1, precision 4 decimal places)
    sdg1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg9: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg10: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg11: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg12: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg13: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg14: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg15: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg16: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    sdg17: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    predicted: Mapped[bool] = mapped_column(Boolean, default=False)
    last_predicted_goal: Mapped[int] = mapped_column(default=0)

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

    def __repr__(self):
        return (
            f"<SDGPrediction(prediction_id={self.prediction_id}, "
            f"publication_id={self.publication_id}, "
            f"prediction_model={self.prediction_model}, "
            f"sdg1={self.sdg1}, sdg2={self.sdg2}, sdg3={self.sdg3}, sdg4={self.sdg4}, "
            f"sdg5={self.sdg5}, sdg6={self.sdg6}, sdg7={self.sdg7}, sdg8={self.sdg8}, "
            f"sdg9={self.sdg9}, sdg10={self.sdg10}, sdg11={self.sdg11}, sdg12={self.sdg12}, "
            f"sdg13={self.sdg13}, sdg14={self.sdg14}, sdg15={self.sdg15}, sdg16={self.sdg16}, "
            f"sdg17={self.sdg17}, predicted={self.predicted}, "
            f"last_predicted_goal={self.last_predicted_goal})>"
        )

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

from models.base import Base


class SDGPrediction(Base):
    __tablename__ = "sdg_predictions"
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(
        Integer, ForeignKey("publications.publication_id"), primary_key=True
    )
    publication = relationship("Publication", back_populates="sdg_predictions")
    prediction_model = Column(String(255), nullable=False, default="")

    # Columns for each SDG goal prediction (values from 0 to 1, precision 4 decimal places)
    # Set default=0.0 for each SDG goal prediction column
    sdg1 = Column(Float(precision=4), default=0.0)
    sdg2 = Column(Float(precision=4), default=0.0)
    sdg3 = Column(Float(precision=4), default=0.0)
    sdg4 = Column(Float(precision=4), default=0.0)
    sdg5 = Column(Float(precision=4), default=0.0)
    sdg6 = Column(Float(precision=4), default=0.0)
    sdg7 = Column(Float(precision=4), default=0.0)
    sdg8 = Column(Float(precision=4), default=0.0)
    sdg9 = Column(Float(precision=4), default=0.0)
    sdg10 = Column(Float(precision=4), default=0.0)
    sdg11 = Column(Float(precision=4), default=0.0)
    sdg12 = Column(Float(precision=4), default=0.0)
    sdg13 = Column(Float(precision=4), default=0.0)
    sdg14 = Column(Float(precision=4), default=0.0)
    sdg15 = Column(Float(precision=4), default=0.0)
    sdg16 = Column(Float(precision=4), default=0.0)
    sdg17 = Column(Float(precision=4), default=0.0)
    predicted = Column(Boolean, default=False)
    last_predicted_goal = Column(Integer, default=0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        onupdate=lambda: datetime.now(time_zone_settings.ZURICH_TZ),
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<SDGPrediction(prediction_id={self.prediction_id},"
            f"<SDGPrediction(publication_id={self.publication_id}, "
            f"<SDGPrediction(prediction_model={self.prediction_model}, "
            f"sdg1={self.sdg1}, sdg2={self.sdg2}, sdg3={self.sdg3}, sdg4={self.sdg4}, "
            f"sdg5={self.sdg5}, sdg6={self.sdg6}, sdg7={self.sdg7}, sdg8={self.sdg8}, "
            f"sdg9={self.sdg9}, sdg10={self.sdg10}, sdg11={self.sdg11}, sdg12={self.sdg12}, "
            f"sdg13={self.sdg13}, sdg14={self.sdg14}, sdg15={self.sdg15}, sdg16={self.sdg16}, "
            f"sdg17={self.sdg17}, predicted={self.predicted}, last_predicted_goal={self.last_predicted_goal})>"
        )

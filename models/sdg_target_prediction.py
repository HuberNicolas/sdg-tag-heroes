from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base
from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()


class SDGTargetPrediction(Base):
    __tablename__ = "sdg_target_predictions"

    target_prediction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.publication_id"), nullable=False)

    # Relationships
    publication: Mapped["Publication"] = relationship("Publication", back_populates="sdg_target_predictions")

    prediction_model: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    # Columns for each SDG target prediction (values from 0 to 1, precision 4 decimal places)
    target1_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target1_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target1_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target1_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target1_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target1_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target1_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target2_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target2_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target3_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_9: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target3_d: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target4_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target4_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target5_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target5_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target6_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target6_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target7_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target7_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target7_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target7_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target7_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target8_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_9: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_10: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target8_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target9_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target9_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target10_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target10_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target11_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target11_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target12_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target12_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target13_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target13_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target13_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target13_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target13_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target14_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target14_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target15_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_9: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target15_c: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target16_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_9: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_10: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_a: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target16_b: Mapped[float] = mapped_column(Float(precision=4), default=0.0)

    target17_1: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_2: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_3: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_4: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_5: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_6: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_7: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_8: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_9: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_10: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_11: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_12: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_13: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_14: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_15: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_16: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_17: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_18: Mapped[float] = mapped_column(Float(precision=4), default=0.0)
    target17_19: Mapped[float] = mapped_column(Float(precision=4), default=0.0)


    predicted: Mapped[bool] = mapped_column(Boolean, default=False)
    last_predicted_target: Mapped[str] = mapped_column(String(255), default="No prediction made")

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
            f"<SDGTargetPrediction(prediction_id={self.target_prediction_id}, "
            f"publication_id={self.publication_id}, "
            f"prediction_model={self.prediction_model}, "
            f"predicted={self.predicted}, "
            f"last_predicted_target={self.last_predicted_target})>"
        )

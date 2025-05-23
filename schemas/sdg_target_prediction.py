from datetime import datetime
from typing import Dict

from pydantic import BaseModel


class SDGTargetPredictionSchemaBase(BaseModel):
    target_prediction_id: int
    publication_id: int
    prediction_model: str
    predicted: bool
    last_predicted_target: str
    target_predictions: Dict[str, float]  # Dictionary holding all 168 targets as key-value pairs

    model_config = {
        "from_attributes": True
    }


class SDGTargetPredictionSchemaFull(SDGTargetPredictionSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

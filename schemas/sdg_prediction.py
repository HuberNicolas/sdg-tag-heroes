from datetime import datetime
from pydantic import BaseModel

class SDGPredictionSchemaBase(BaseModel):
    prediction_id: int
    publication_id: int
    prediction_model: str
    sdg1: float
    sdg2: float
    sdg3: float
    sdg4: float
    sdg5: float
    sdg6: float
    sdg7: float
    sdg8: float
    sdg9: float
    sdg10: float
    sdg11: float
    sdg12: float
    sdg13: float
    sdg14: float
    sdg15: float
    sdg16: float
    sdg17: float
    predicted: bool
    last_predicted_goal: int

    model_config = {
        "from_attributes": True
    }


class SDGPredictionSchemaFull(SDGPredictionSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

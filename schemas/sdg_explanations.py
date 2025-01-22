from typing import List, Optional
from pydantic import BaseModel, Field

class ExplanationSchema(BaseModel):
    mongodb_id: str
    sql_id: int
    oai_identifier: str
    input_tokens: List[str]
    token_scores: List[List[float]]
    base_values: List[float]
    xai_method: str
    prediction_model: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

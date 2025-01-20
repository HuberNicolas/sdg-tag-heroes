from typing import List
from pydantic import BaseModel

class TokenScore(BaseModel):
    input_token: str
    token_score: float

class ExplanationSchema(BaseModel):
    id: str
    input_tokens: List[str]
    token_scores: List[List[float]]
    base_values: List[float]
    xai_method: str
    prediction_model: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

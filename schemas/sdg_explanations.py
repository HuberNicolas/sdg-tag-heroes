from typing import List, Optional
from pydantic import BaseModel, Field

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

    class Config:
        orm_mode = True

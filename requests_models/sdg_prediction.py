from pydantic import BaseModel
from typing import List, Optional

class SDGPredictionsIdsRequest(BaseModel):
    sdg_predictions_ids: List[int]

class SDGPredictionsPublicationsIdsRequest(BaseModel):
    publications_ids: Optional[List[int]]



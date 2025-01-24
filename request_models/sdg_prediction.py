from typing import List, Optional

from pydantic import BaseModel


class SDGPredictionsIdsRequest(BaseModel):
    sdg_predictions_ids: List[int]

class SDGPredictionsPublicationsIdsRequest(BaseModel):
    publications_ids: Optional[List[int]]



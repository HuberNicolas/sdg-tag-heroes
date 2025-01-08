from pydantic import BaseModel
from typing import List, Optional


class PublicationIdsRequest(BaseModel):
    publication_ids: List[int]

class UserIdsRequest(BaseModel):
    user_ids: List[int]

class SDGPredictionsIdsRequest(BaseModel):
    sdg_predictions_ids: List[int]

class SDGPredictionsPublicationsIdsRequest(BaseModel):
    publications_ids: Optional[List[int]]



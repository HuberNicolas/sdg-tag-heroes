from pydantic import BaseModel
from typing import List

class PublicationIdsRequest(BaseModel):
    publication_ids: List[int]

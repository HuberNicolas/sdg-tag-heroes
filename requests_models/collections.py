from typing import List
from pydantic import BaseModel


class CollectionsIdsRequest(BaseModel):
    collection_ids: List[int]

    class Config:
        from_attributes = True

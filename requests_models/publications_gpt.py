from typing import List
from pydantic import BaseModel


class PublicationIdsRequest(BaseModel):
    publication_ids: List[int]

    class Config:
        from_attributes = True

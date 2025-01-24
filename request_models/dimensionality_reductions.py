from typing import List

from pydantic import BaseModel

class UserCoordinatesRequest(BaseModel):
    sdg: int # (1..17)
    level: int # (1..3)
    user_query: str

    class Config:
        from_attributes = True


class DimensionalityReductionPublicationIdsRequest(BaseModel):
    publication_ids: List[int]

    class Config:
        from_attributes = True

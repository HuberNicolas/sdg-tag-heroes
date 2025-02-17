from typing import List, Optional

from pydantic import BaseModel

class UserCoordinatesRequest(BaseModel):
    sdg: Optional[int] = None # (1..17)
    level: Optional[int] = None # (1..3)
    user_query: str

    class Config:
        from_attributes = True


class DimensionalityReductionPublicationIdsRequest(BaseModel):
    publication_ids: List[int]

    class Config:
        from_attributes = True

from typing import List
from pydantic import BaseModel

class UserIdsRequest(BaseModel):
    user_ids: List[int]

    class Config:
        from_attributes = True

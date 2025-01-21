from typing import List
from pydantic import BaseModel


class UserIdsRequest(BaseModel):
    user_ids: List[int]

    class Config:
        # Ensure that attribute names match the model's variable names
        from_attributes = True

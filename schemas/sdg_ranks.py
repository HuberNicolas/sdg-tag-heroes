from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Union


class SDGRankSchemaBase(BaseModel):
    rank_id: int
    sdg_goal_id: int
    tier: int
    name: str
    description: Optional[str] = None
    xp_required: float

    model_config = {
        "from_attributes": True
    }


class SDGRankSchemaFull(SDGRankSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Not directly derived derived from models
class UsersSDGRankSchemaBase(BaseModel):
    user_id: Optional[int]
    user: Optional[Union["UserSchemaBase", "UserSchemaFull"]]
    ranks: List[SDGRankSchemaFull]  # List of SDG ranks for that user

    model_config = {
        "from_attributes": True
    }

from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum

# TODO: Outsource
class VoteType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class VoteSchemaBase(BaseModel):
    vote_id: int
    user_id: int
    sdg_user_label_id: Optional[int]
    annotation_id: Optional[int]
    vote_type: VoteType
    score: float

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class VoteSchemaCreate(BaseModel):
    user_id: int
    sdg_user_label_id: Optional[int] = None
    annotation_id: Optional[int] = None
    vote_type: VoteType
    score: float

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class VoteSchemaFull(VoteSchemaBase):
    created_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

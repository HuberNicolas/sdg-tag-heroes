from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from enums.enums import VoteType


class VoteSchemaBase(BaseModel):
    vote_id: int
    user_id: int
    sdg_user_label_id: Optional[int]
    annotation_id: Optional[int]
    vote_type: VoteType
    score: float

    model_config = {
        "from_attributes": True
    }


class VoteSchemaFull(VoteSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

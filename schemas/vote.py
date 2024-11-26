from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator
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

    @model_validator(mode="after")
    def validate_vote_target(self):
        """
        Ensure that exactly one of `sdg_user_label_id` or `annotation_id` is provided.
        """
        if (self.sdg_user_label_id is None) == (self.annotation_id is None):
            raise ValueError("Exactly one of `sdg_user_label_id` or `annotation_id` must be provided.")
        return self


class VoteSchemaFull(VoteSchemaBase):
    created_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

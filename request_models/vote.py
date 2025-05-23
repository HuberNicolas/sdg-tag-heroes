from typing import Optional

from pydantic import BaseModel, Field

from enums.enums import VoteType


class VoteCreateRequest(BaseModel):
    user_id: int
    sdg_user_label_id: Optional[int] = Field(default=None, description="The ID of the SDGUserLabel being voted on (optional).")
    annotation_id: Optional[int] = Field(default=None, description="The ID of the Annotation being voted on (optional).")
    vote_type: VoteType
    score: float


    class Config:
        from_attributes = True

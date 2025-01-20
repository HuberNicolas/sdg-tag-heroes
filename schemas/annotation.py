from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel

from schemas.vote import VoteSchemaBase, VoteSchemaFull

class AnnotationSchemaBase(BaseModel):
    annotation_id: int
    user_id: int
    sdg_user_label_id: Optional[int]
    decision_id: Optional[int]
    labeler_score: float
    comment: str
    votes: List[Union[VoteSchemaBase, VoteSchemaFull]]

    model_config = {
        "from_attributes": True
    }

class AnnotationSchemaFull(AnnotationSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel


class SDGUserLabelSchemaBase(BaseModel):
    label_id: int
    user_id: int
    proposed_label: Optional[int]
    voted_label: int
    abstract_section: Optional[str]
    comment: Optional[str]
    annotations: List[Union["AnnotationSchemaBase", "AnnotationSchemaFull"]]
    votes: List[Union["VoteSchemaBase", "VoteSchemaFull"]]
    label_decisions: List[Union["SDGLabelDecisionSchemaBase", "SDGLabelDecisionSchemaFull"]]

    model_config = {
        "from_attributes": True
    }


class SDGUserLabelSchemaFull(SDGUserLabelSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from schemas.vote import VoteSchemaFull


class DecisionType(str, Enum):
    CONSENSUS_MAJORITY = "Consensus Majority"
    CONSENSUS_TECHNOCRATIC = "Consensus Technocratic"
    EXPERT_DECISION = "Expert Decision"

class SDGUserLabelSchemaBase(BaseModel):
    label_id: int
    user_id: int
    proposed_label: Optional[int]
    voted_label: int
    abstract_section: Optional[str] = None
    comment: Optional[str] = None

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

class SDGUserLabelSchemaFull(SDGUserLabelSchemaBase):
    labeled_at: datetime
    created_at: datetime
    updated_at: datetime
    votes: Optional[list[VoteSchemaFull]] = None

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGUserLabelSchemaCreate(BaseModel):
    proposed_label: int = None
    voted_label: int
    abstract_section: Optional[str] = None
    comment: Optional[str] = None



    decision_id: Optional[int] = None

    publication_id: Optional[int] = None
    # suggested_label: Optional[int] = None
    decision_type: Optional[DecisionType] = None

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }





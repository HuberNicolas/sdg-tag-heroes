from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel

from enums.enums import DecisionType, ScenarioType


class SDGLabelDecisionSchemaBase(BaseModel):
    decision_id: int
    publication_id: int
    suggested_label: int
    decided_label: int
    decision_type: DecisionType
    scenario_type: ScenarioType
    expert_id: Optional[int]
    history_id: Optional[int]
    comment: Optional[str]
    annotations: List[Union["AnnotationSchemaBase", "AnnotationSchemaFull"]]

    model_config = {
        "from_attributes": True
    }


class SDGLabelDecisionSchemaFull(SDGLabelDecisionSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class SDGLabelDecisionSchemaExtended(SDGLabelDecisionSchemaBase):
    created_at: datetime
    updated_at: datetime

    # Include all user labels associated with the decision
    user_labels: List["SDGUserLabelSchemaFull"]

    # Include all annotations directly attached to the decision
    annotations: List["AnnotationSchemaFull"]

    model_config = {
        "from_attributes": True
    }

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class SDGLabelDecisionSchemaBase(BaseModel):
    decision_id: int
    history_id: int
    comment: Optional[str]

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGLabelDecisionSchemaFull(SDGLabelDecisionSchemaBase):
    decided_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

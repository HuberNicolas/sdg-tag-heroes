from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union


class SDGTargetSchemaBase(BaseModel):
    id: int
    index: str
    text: str
    color: str
    target_vector_index: int
    icon: Optional[str] = None  # Default to None if missing
    sdg_goal: Optional[Union["SDGGoalSchemaBase", "SDGGoalSchemaFull"]]  # Nested relationship for goal

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGTargetSchemaFull(SDGTargetSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

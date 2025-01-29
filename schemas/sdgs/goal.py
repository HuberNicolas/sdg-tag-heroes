from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class SDGGoalSchemaBase(BaseModel):
    id: int
    index: int
    name: str
    color: str
    short_title: str
    keywords: str
    explanation: str
    icon: Optional[str] = None  # Default to None if missing
    sdg_targets: Optional[List[Union["SDGTargetSchemaBase", "SDGTargetSchemaFull"]]] = Field(list) # Todo: Double check if Field(list) is fine

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGGoalSchemaFull(SDGGoalSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

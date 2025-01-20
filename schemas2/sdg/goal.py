from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Union

from schemas import SDGTargetSchemaBase, SDGTargetSchemaFull


class SDGGoalSchemaBase(BaseModel):
    id: int
    index: int
    name: str
    color: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

class SDGGoalSchemaFull(SDGGoalSchemaBase):
    icon: Optional[str] = None  # Default to None if missing
    sdg_targets: Optional[List[Union[SDGTargetSchemaBase, SDGTargetSchemaFull]]] = Field(default_factory=list)


model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

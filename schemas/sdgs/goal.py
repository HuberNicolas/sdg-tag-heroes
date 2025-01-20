from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Union

from schemas.sdgs.target import SDGTargetSchemaBase, SDGTargetSchemaFull

class SDGGoalSchemaBase(BaseModel):
    id: int
    index: int
    name: str
    color: str
    icon: Optional[str] = None  # Default to None if missing
    sdg_targets: Optional[List[Union[SDGTargetSchemaBase, SDGTargetSchemaFull]]] = Field(default_factory=list)

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGGoalSchemaFull(SDGGoalSchemaBase):

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

from pydantic import BaseModel
from typing import List, Optional

from schemas.sdg_target import SDGTargetSchemaFull


class SDGGoalSchemaBase(BaseModel):
    id: int
    index: int
    name: str
    color: str
    icon: Optional[str]

    class Config:
        from_attributes = True

class SDGGoalSchemaFull(SDGGoalSchemaBase):
    sdg_targets: Optional[List[SDGTargetSchemaFull]]  # Full relationship for targets

    class Config:
        from_attributes = True

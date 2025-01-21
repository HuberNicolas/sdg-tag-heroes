from datetime import datetime
from typing import List, Union
from pydantic import BaseModel

from schemas.achievement import AchievementSchemaBase, AchievementSchemaFull

class InventorySchemaBase(BaseModel):
    inventory_id: int
    user_id: int
    achievements: List[Union[AchievementSchemaBase, AchievementSchemaFull]]

    model_config = {
        "from_attributes": True
    }


class InventorySchemaFull(InventorySchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

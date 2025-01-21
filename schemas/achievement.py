from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel

from schemas.inventory_achievement_association import InventoryAchievementAssociationSchemaBase, InventoryAchievementAssociationSchemaFull

class AchievementSchemaBase(BaseModel):
    achievement_id: int
    name: str
    description: Optional[str]
    inventory_achievements: List[Union[InventoryAchievementAssociationSchemaBase, InventoryAchievementAssociationSchemaFull]]

    model_config = {
        "from_attributes": True
    }


class AchievementSchemaFull(AchievementSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

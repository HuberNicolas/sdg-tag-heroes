from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InventoryAchievementAssociationSchemaBase(BaseModel):
    id: int
    inventory_id: int
    achievement_id: int
    comment: Optional[str]
    added_at: datetime

    model_config = {
        "from_attributes": True
    }


class InventoryAchievementAssociationSchemaFull(InventoryAchievementAssociationSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

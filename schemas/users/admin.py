from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.users.user import UserSchemaBase


class AdminSchemaBase(BaseModel):
    admin_id: int

    model_config = {
        "from_attributes": True
    }


class AdminSchemaFull(AdminSchemaBase):
    user: Optional[UserSchemaBase]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.users.user import UserSchemaBase

class ExpertSchemaBase(BaseModel):
    expert_id: int
    expert_score: float

    model_config = {
        "from_attributes": True
    }


class ExpertSchemaFull(ExpertSchemaBase):
    user: Optional[UserSchemaBase]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

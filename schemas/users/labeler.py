from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from schemas.users.user import UserSchemaBase

class LabelerSchemaBase(BaseModel):
    labeler_id: int
    labeler_score: float

    model_config = {
        "from_attributes": True
    }


class LabelerSchemaFull(LabelerSchemaBase):
    user: Optional[UserSchemaBase]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

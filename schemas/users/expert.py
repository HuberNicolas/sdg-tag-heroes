from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel

from schemas.users.user import UserSchemaBase, UserSchemaFull

class ExpertSchemaBase(BaseModel):
    expert_id: int
    expert_score: float
    user: Optional[Union[UserSchemaBase, UserSchemaFull]]

    model_config = {
        "from_attributes": True
    }


class ExpertSchemaFull(ExpertSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

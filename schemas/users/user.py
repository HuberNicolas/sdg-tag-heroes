from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

from enums.enums import UserRole

class UserSchemaBase(BaseModel):
    user_id: int
    nickname: Optional[str]
    email: EmailStr
    is_active: bool
    roles: List[UserRole]

    model_config = {
        "from_attributes": True
    }


class UserSchemaFull(UserSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

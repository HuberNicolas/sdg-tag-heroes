from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, model_validator
from enum import Enum

from models.users.user import UserRole



class UserRoleEnum(str, Enum):
    user = UserRole.USER.value
    admin = UserRole.ADMIN.value
    labeler = UserRole.LABELER.value
    expert = UserRole.EXPERT.value

class UserSchemaBase(BaseModel):
    user_id: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

class UserSchemaFull(UserSchemaBase):
    email: str
    roles: List[UserRole]
    is_active: bool

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }



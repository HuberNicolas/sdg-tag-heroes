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

    class Config:
        orm_mode = True

class UserSchemaFull(UserSchemaBase):
    email: str
    roles: List[UserRole]
    is_active: bool

    class Config:
        orm_mode = True



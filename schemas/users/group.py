from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class GroupSchemaBase(BaseModel):
    group_id: int
    name: str
    members: List[Union["UserSchemaBase", "UserSchemaFull"]]  # List of user objects as schemas

    model_config = {
        "from_attributes": True
    }


class GroupSchemaFull(GroupSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel


class AdminSchemaBase(BaseModel):
    admin_id: int
    user: Optional[Union["UserSchemaBase", "UserSchemaFull"]]

    model_config = {
        "from_attributes": True
    }


class AdminSchemaFull(AdminSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

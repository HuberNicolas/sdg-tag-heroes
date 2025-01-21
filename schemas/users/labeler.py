from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel


class LabelerSchemaBase(BaseModel):
    labeler_id: int
    labeler_score: float
    user: Optional[Union["UserSchemaBase", "UserSchemaFull"]]

    model_config = {
        "from_attributes": True
    }


class LabelerSchemaFull(LabelerSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from datetime import datetime

from pydantic import BaseModel


class SDGLabelHistorySchemaBase(BaseModel):
    history_id: int
    active: bool

    model_config = {
        "from_attributes": True
    }


class SDGLabelHistorySchemaFull(SDGLabelHistorySchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

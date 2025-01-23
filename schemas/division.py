from datetime import datetime

from pydantic import BaseModel


class DivisionSchemaBase(BaseModel):
    division_id: int
    division_name: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class DivisionSchemaFull(DivisionSchemaBase):
    division_setSpec: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

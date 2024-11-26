from pydantic import BaseModel
from typing import Optional

class SDGTargetSchemaBase(BaseModel):
    id: int
    index: str
    text: str
    color: str
    target_vector_index: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

class SDGTargetSchemaFull(SDGTargetSchemaBase):
    icon: Optional[str] = None  # Default to None if missing

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

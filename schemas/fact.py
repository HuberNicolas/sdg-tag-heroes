from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FactSchemaBase(BaseModel):
    fact_id: int
    content: Optional[str]
    publication_id: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class FactSchemaFull(FactSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

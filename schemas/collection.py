from datetime import datetime
from typing import List

from pydantic import BaseModel


class CollectionSchemaBase(BaseModel):
    collection_id: int
    topic_id: int  # Unique topic_id
    count: int
    name: str
    short_name: str
    representation: List[str]
    aspect1: List[str] # Same assumption for these JSON fields
    aspect2: List[str]
    aspect3: List[str]

    model_config = {
        "from_attributes": True
    }

class CollectionSchemaFull(CollectionSchemaBase):
    created_at: datetime
    updated_at: datetime

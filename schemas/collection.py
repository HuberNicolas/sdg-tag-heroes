from datetime import datetime
from typing import List
from pydantic import BaseModel

class CollectionSchemaBase(BaseModel):
    collection_id: int
    count: int
    name: str
    short_name: str
    representation: List[str]  # Assuming the JSON list of strings is parsed into a Python list
    aspect1: List[str]         # Same assumption for these JSON fields
    aspect2: List[str]
    aspect3: List[str]

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy objects

class CollectionSchemaFull(CollectionSchemaBase):
    created_at: datetime
    updated_at: datetime

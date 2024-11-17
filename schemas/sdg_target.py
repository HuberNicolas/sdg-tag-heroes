from pydantic import BaseModel
from typing import Optional

class SDGTargetSchemaBase(BaseModel):
    id: int
    index: str
    text: str
    color: str
    targetVectorIndex: int

    class Config:
        from_attributes = True

class SDGTargetSchemaFull(SDGTargetSchemaBase):
    icon: Optional[str]  # Include the icon field in the full schema

    class Config:
        from_attributes = True

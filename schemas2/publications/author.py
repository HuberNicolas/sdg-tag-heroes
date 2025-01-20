from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuthorSchemaBase(BaseModel):
    author_id: int
    orcid_id: Optional[str]

    class Config:
        from_attributes = True



class AuthorSchemaFull(AuthorSchemaBase):
    name: Optional[str]
    lastname: Optional[str]
    surname: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

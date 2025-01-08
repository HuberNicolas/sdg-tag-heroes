from datetime import datetime
from typing import Optional, Union, List

from pydantic import BaseModel

from schemas.publications.author import AuthorSchemaBase, AuthorSchemaFull


class PublicationSchemaBase(BaseModel):
    publication_id: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

class PublicationSchemaFull(PublicationSchemaBase):
    publication_id: int
    oai_identifier: str
    oai_identifier_num: int
    title: Optional[str]
    description: Optional[str]
    publisher: Optional[str]
    year: Optional[int]
    authors: Optional[List[Union[AuthorSchemaBase, AuthorSchemaFull]]]

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

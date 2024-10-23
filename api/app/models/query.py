from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator


class PublicationQuery(BaseModel):
    title: Optional[str] = None
    author_name: Optional[str] = None
    year: Optional[int] = None
    faculty_id: Optional[int] = None

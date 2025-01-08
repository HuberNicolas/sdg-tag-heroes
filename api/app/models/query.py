from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator


class PublicationQuery(BaseModel):
    title: Optional[str] = None
    author_name: Optional[str] = None
    year: Optional[int] = None
    faculty_id: Optional[int] = None


class SimilarityQueryRequest(BaseModel):
    user_query: str
    publication_ids: Optional[List[int]] = None  # Optional list of publication IDs to restrict the search


class SkillsRequest(BaseModel):
    skills: str

class InterestsRequest(BaseModel):
    interests: str

class UserCoordinatesRequest(BaseModel):
    sdg: int # (1..17)
    level: int # (1..3)
    user_query: str


class AnnotationScoreRequest(BaseModel):
    passage: str = Field(..., description="The marked passage.")
    annotation: str = Field(..., description="The user's comment.")
    sdg_label: int = Field(..., ge=1, le=17, description="The SDG label index (1 to 17).")

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



class SDGFilterQuery(BaseModel):
    sdg_field: Optional[str] = Field(
        None,
        description="The SDG field to filter by (e.g., 'sdg1', 'sdg2', ..., 'sdg17')."
    )
    lower_limit: float = Field(
        0.98,
        ge=0.0,
        le=1.0,
        description="Lower limit for filtering SDG field values (default: 0.98)."
    )
    upper_limit: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Upper limit for filtering SDG field values (default: 1.0)."
    )
    no_high_predictions: Optional[int] = Field(
        None,
        ge=0,
        description=(
            "Minimum number of other SDG fields (besides sdg_field) that must "
            "satisfy the range condition to include the prediction. Default is None."
        )
    )

    @validator("sdg_field")
    def validate_sdg_field(cls, value):
        valid_sdg_fields = {
            "sdg1", "sdg2", "sdg3", "sdg4", "sdg5", "sdg6", "sdg7", "sdg8",
            "sdg9", "sdg10", "sdg11", "sdg12", "sdg13", "sdg14", "sdg15", "sdg16", "sdg17"
        }
        if value and value not in valid_sdg_fields:
            raise ValueError(f"Invalid SDG field. Allowed values are: {', '.join(valid_sdg_fields)}.")
        return value

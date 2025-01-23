from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# Requests for specific IDs
class PublicationIdsRequest(BaseModel):
    publication_ids: List[int] = Field(..., description="List of publication IDs.")


class UserIdsRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs.")


class SDGPredictionsIdsRequest(BaseModel):
    sdg_predictions_ids: List[int] = Field(..., description="List of SDG prediction IDs.")


class SDGPredictionsPublicationsIdsRequest(BaseModel):
    publications_ids: Optional[List[int]] = Field(
        None, description="Optional list of publication IDs for SDG predictions."
    )


# Queries and filters
class PublicationQuery(BaseModel):
    title: Optional[str] = Field(None, description="Title of the publication.")
    author_name: Optional[str] = Field(None, description="Name of the author.")
    year: Optional[int] = Field(None, description="Publication year.")
    faculty_id: Optional[int] = Field(None, description="Faculty ID associated with the publication.")


class SimilarityQueryRequest(BaseModel):
    user_query: str = Field(..., description="User-provided query for similarity search.")
    publication_ids: Optional[List[int]] = Field(
        None, description="Optional list of publication IDs to restrict the search."
    )


class SkillsRequest(BaseModel):
    skills: str = Field(..., description="Skills input by the user.")


class InterestsRequest(BaseModel):
    interests: str = Field(..., description="Interests input by the user.")


class UserCoordinatesRequest(BaseModel):
    sdg: int = Field(..., ge=1, le=17, description="The SDG index (1 to 17).")
    level: int = Field(..., ge=1, le=3, description="The level index (1 to 3).")
    user_query: str = Field(..., description="Query related to the user's SDG and level.")


class AnnotationScoreRequest(BaseModel):
    passage: str = Field(..., description="The marked passage for annotation.")
    annotation: str = Field(..., description="The user's annotation or comment.")
    sdg_label: int = Field(
        ..., ge=1, le=17, description="The SDG label index (1 to 17) associated with the annotation."
    )


class SDGFilterQuery(BaseModel):
    sdg_field: Optional[str] = Field(
        None, description="The SDG field to filter by (e.g., 'sdg1', ..., 'sdg17')."
    )
    lower_limit: float = Field(
        0.98, ge=0.0, le=1.0, description="Lower limit for filtering SDG field values (default: 0.98)."
    )
    upper_limit: float = Field(
        1.0, ge=0.0, le=1.0, description="Upper limit for filtering SDG field values (default: 1.0)."
    )
    no_high_predictions: Optional[int] = Field(
        None,
        ge=0,
        description=(
            "Minimum number of other SDG fields (besides sdg_field) that must "
            "satisfy the range condition to include the prediction. Default is None."
        )
    )

    @field_validator("sdg_field")
    def validate_sdg_field(cls, value):
        valid_sdg_fields = {f"sdg{i}" for i in range(1, 18)}
        if value and value not in valid_sdg_fields:
            raise ValueError(f"Invalid SDG field. Allowed values are: {', '.join(valid_sdg_fields)}.")
        return value


from pydantic import BaseModel
from typing import List, Optional


class PublicationIdsRequest(BaseModel):
    publication_ids: List[int]

class UserIdsRequest(BaseModel):
    user_ids: List[int]

class SDGPredictionsIdsRequest(BaseModel):
    sdg_predictions_ids: List[int]

class SDGPredictionsPublicationsIdsRequest(BaseModel):
    publications_ids: Optional[List[int]]



from datetime import datetime
from typing import Optional, Union, List
from pydantic import BaseModel



from schemas.author import AuthorSchemaBase, AuthorSchemaFull




from schemas.sdg_label_summary import SDGLabelSummarySchema
from schemas.sdg_prediction import SDGPredictionSchema
from schemas.sdg_target_prediction import SDGTargetPredictionSchema
from schemas.dimensionality_reduction import DimensionalityReductionSchema
from schemas.publication_cluster import PublicationClusterSchema
from schemas.fact import FactSchema
from schemas.summary import SummarySchema

from schemas.faculty import FacultySchemaBase, FacultySchemaFull
from schemas.institute import InstituteSchemaBase, InstituteSchemaFull
from schemas.division import DivisionSchemaBase, DivisionSchemaFull


class PublicationSchemaBase(BaseModel):
    publication_id: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class PublicationSchemaFull(PublicationSchemaBase):
    oai_identifier: str
    oai_identifier_num: int
    title: Optional[str]
    description: Optional[str]
    publisher: Optional[str]
    date: Optional[str]
    year: Optional[int]
    source: Optional[str]
    language: Optional[str]
    format: Optional[str]
    embedded: bool
    set_spec: Optional[str]
    is_dim_reduced: bool

    authors: Optional[List[Union[AuthorSchemaBase, AuthorSchemaFull]]]
    sdg_label_summary: Optional[SDGLabelSummarySchema]
    sdg_predictions: Optional[List[SDGPredictionSchema]]
    sdg_target_predictions: Optional[List[SDGTargetPredictionSchema]]
    dimensionality_reductions: Optional[List[DimensionalityReductionSchema]]
    # clusters: Optional[List[PublicationClusterSchema]]
    # fact: Optional[FactSchema]
    # summary: Optional[SummarySchema]

    faculty_id: Optional[int]
    faculty: Optional[List[Union[FacultySchemaBase, FacultySchemaFull]]]
    institute_id: Optional[int]
    institute: Optional[List[Union[InstituteSchemaBase, InstituteSchemaFull]]]
    division_id: Optional[int]
    division: Optional[List[Union[DivisionSchemaBase, DivisionSchemaFull]]]

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

from datetime import datetime
from typing import Optional, Union, List
from pydantic import BaseModel

class PublicationSchemaBase(BaseModel):
    publication_id: int
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

    authors: Optional[List[Union["AuthorSchemaBase", "AuthorSchemaFull"]]]
    sdg_label_summary: Optional[List[Union["SDGLabelSummarySchemaBase", "SDGLabelSummarySchemaFull"]]]
    sdg_predictions: Optional[List[Union["SDGPredictionSchemaBase", "SDGPredictionSchemaFull"]]]
    sdg_target_predictions: Optional[List[Union["SDGTargetPredictionSchemaBase", "SDGTargetPredictionSchemaFull"]]]
    dimensionality_reductions: Optional[List[Union["DimensionalityReductionSchemaBase", "DimensionalityReductionSchemaFull"]]]

    clusters: Optional[List[Union["PublicationClusterSchemaBase", "PublicationClusterSchemaFull"]]]
    fact: Optional[Union["FactSchemaBase", "FactSchemaFull"]]
    summary: Optional[Union["SummarySchemaBase", "SummarySchemaFull"]]

    faculty_id: Optional[int]
    faculty: Optional[List[Union["FacultySchemaBase", "FacultySchemaFull"]]]
    institute_id: Optional[int]
    institute: Optional[List[Union["InstituteSchemaBase", "InstituteSchemaFull"]]]
    division_id: Optional[int]
    division: Optional[List[Union["DivisionSchemaBase", "DivisionSchemaFull"]]]

    collection_id: Optional[int]
    collection: Optional[Union["CollectionSchemaBase", "CollectionSchemaFull"]]

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class PublicationSchemaFull(PublicationSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

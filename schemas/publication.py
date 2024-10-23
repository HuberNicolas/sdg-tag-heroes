from pydantic import BaseModel, Field, condecimal, validator
from datetime import datetime
from typing import List, Optional, Union

class SDGPredictionSchemaBase(BaseModel):
    prediction_id: int
    publication_id: int
    prediction_model: str

    class Config:
        from_attributes = True


class SDGPredictionSchemaFull(BaseModel):
    prediction_id: int
    publication_id: int
    prediction_model: str
    sdg1: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg2: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg3: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg4: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg5: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg6: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg7: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg8: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg9: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg10: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg11: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg12: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg13: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg14: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg15: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg16: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    sdg17: condecimal(max_digits=5, decimal_places=4) = Field(0.0)
    predicted: bool = Field(False)
    last_predicted_goal: int = Field(0)
    created_at: datetime
    updated_at: datetime

    # Validator to round all float values for SDGs
    @validator('sdg1', 'sdg2', 'sdg3', 'sdg4', 'sdg5', 'sdg6', 'sdg7', 'sdg8', 'sdg9',
               'sdg10', 'sdg11', 'sdg12', 'sdg13', 'sdg14', 'sdg15', 'sdg16', 'sdg17', pre=True)
    def round_sdg_values(cls, v):
        if isinstance(v, float):
            return round(v, 4)
        return v

    class Config:
        from_attributes = True
        orm_mode = True  # This allows Pydantic to work with SQLAlchemy models directly

class FacultySchemaFull(BaseModel):
    faculty_id: int
    faculty_setSpec: str
    faculty_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FacultySchemaBase(BaseModel):
    faculty_id: int

    class Config:
        from_attributes = True

class InstituteSchemaFull(BaseModel):
    institute_id: int
    institute_setSpec: str
    institute_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InstituteSchemaBase(BaseModel):
    institute_id: int

    class Config:
        from_attributes = True

class DivisionSchemaFull(BaseModel):
    division_id: int
    division_setSpec: str
    division_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DivisionSchemaBase(BaseModel):
    division_id: int

    class Config:
        from_attributes = True

class DimRedSchemaFull(BaseModel):
    dim_red_id: int
    umap_x_coord: condecimal(max_digits=6, decimal_places=4) = Field(0.0)
    umap_y_coord: condecimal(max_digits=6, decimal_places=4) = Field(0.0)
    created_at: datetime
    updated_at: datetime

    # Validator to round all float values for SDGs
    @validator('umap_x_coord', 'umap_y_coord', pre=True)
    def round_sdg_values(cls, v):
        if isinstance(v, float):
            return round(v, 4)
        return v

    class Config:
        from_attributes = True

class DimRedSchemaBase(BaseModel):
    dim_red_id: int

    class Config:
        from_attributes = True

class AuthorSchemaFull(BaseModel):
    author_id: int
    name: Optional[str]
    lastname: Optional[str]
    surname: Optional[str]
    orcid_id: Optional[str]
    # Minimal information to avoid circular dependency
    # publications: Optional[List[int]]  # Only include publication IDs
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AuthorSchemaBase(BaseModel):
    author_id: int
    orcid_id: Optional[str]
    # Minimal information to avoid circular dependency
    # publications: Optional[List[int]]  # Only include publication IDs

    class Config:
        from_attributes = True


class PublicationSchema(BaseModel):
    publication_id: int
    oai_identifier: str
    oai_identifier_num: int
    title: Optional[str]
    description: Optional[str]
    authors: Optional[List[Union[AuthorSchemaBase, AuthorSchemaFull]]]  # Union of base or full schema
    publisher: Optional[str]
    date: Optional[str]
    year: Optional[int]
    source: Optional[str]
    language: Optional[str]
    format: Optional[str]
    sdg_predictions: Optional[List[Union[SDGPredictionSchemaBase, SDGPredictionSchemaFull]]]  # Union for SDG predictions
    embedded: bool = Field(False)
    set_spec: Optional[str]
    faculty: Optional[Union[FacultySchemaBase, FacultySchemaFull]]  # Union for faculty
    institute: Optional[Union[InstituteSchemaBase, InstituteSchemaFull]]  # Union for institute
    division: Optional[Union[DivisionSchemaBase, DivisionSchemaFull]]  # Union for division
    dim_red: Optional[Union[DimRedSchemaBase, DimRedSchemaFull]]  # Union for DimRed
    dimreduced: bool = Field(False)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True




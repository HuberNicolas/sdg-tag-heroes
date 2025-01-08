from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DimensionalityReductionSchemaBase(BaseModel):
    dim_red_id: int
    publication_id: int
    reduction_technique: Optional[str]
    reduction_shorthand: Optional[str]
    sdg: int
    level: int
    x_coord: float
    y_coord: float
    z_coord: Optional[float]


    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class DimensionalityReductionSchemaFull(DimensionalityReductionSchemaBase):
    reduction_details: Optional[str]
    created_at: datetime
    updated_at: datetime


    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

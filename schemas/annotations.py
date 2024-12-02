from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnnotationSchemaBase(BaseModel):
    annotation_id: int
    user_id: int
    sdg_user_label_id: int
    labeler_score: float
    comment: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }



class AnnotationSchemaCreate(BaseModel):
    user_id: int
    sdg_user_label_id: int
    labeler_score: float
    comment: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }



class AnnotationSchemaFull(AnnotationSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


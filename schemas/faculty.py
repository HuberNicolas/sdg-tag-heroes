from datetime import datetime

from pydantic import BaseModel


class FacultySchemaBase(BaseModel):
    faculty_id: int
    faculty_name: str

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class FacultySchemaFull(FacultySchemaBase):
    faculty_setSpec: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

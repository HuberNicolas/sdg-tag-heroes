from datetime import datetime

from pydantic import BaseModel, condecimal, Field, validator


class SDGPredictionSchemaBase(BaseModel):
    prediction_id: int
    publication_id: int
    prediction_model: str

    class Config:
        from_attributes = True


class SDGPredictionSchemaFull(SDGPredictionSchemaBase):
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

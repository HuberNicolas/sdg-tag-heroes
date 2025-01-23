from datetime import datetime
from typing import List

from pydantic import BaseModel


# Not directly derived from models
# Todo: Generate TS type



# Function Output Schemas

###


# API Response Schemas
class MetricSchema(BaseModel):
    metric_type: str
    value: float
    timestamp: datetime

    class Config:
        from_attributes = True  # Enables ORM-style model validation

class PublicationMetricsSchema(BaseModel):
    publication_id: int
    metrics: List[MetricSchema]

    class Config:
        from_attributes = True  # Enables ORM-style model validation

class FilteredMetricsSchema(BaseModel):
    metric_type: str
    order: str
    top_n: int
    metrics: List[MetricSchema]

    class Config:
        from_attributes = True  # Enables ORM-style model validation

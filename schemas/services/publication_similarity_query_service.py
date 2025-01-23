from typing import List, Dict
from pydantic import BaseModel


# Not directly derived from models
# Todo: Generate TS type


# Function Output Schemas
class FunctionResponsePublicationSimilaritySchema(BaseModel):
    publication_id: int
    title: str
    abstract: str
    score: float

class FunctionResponsePublicationsSimilaritySchema(BaseModel):
    query_building_time: float
    search_time: float
    user_query: str
    results: List[FunctionResponsePublicationSimilaritySchema]


# API Response Schemas
class PublicationSimilaritySchema(BaseModel):
    query_building_time: float
    search_time: float
    user_query: str
    results: List[dict]

    class Config:
        from_attributes = True  # Enables ORM-style model validation

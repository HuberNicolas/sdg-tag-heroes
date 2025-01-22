from typing import List
from pydantic import BaseModel

# Not directly derived from models
# Todo: Generate TS type


# GPT Function Output Schemas
class GPTResponseKeywordsSchema(BaseModel):
    keywords: List[str]

class GPTResponseSDGAnalysisSchema(BaseModel):
    relevance: str
    reasoning: str

class GPTResponseFactSchema(BaseModel):
    fact: str

class GPTResponseSummarySchema(BaseModel):
    summary: str

class GPTResponseCollectiveSummarySchema(BaseModel):
    summary: str
    keywords: List[str]

class GPTResponseSkillsQuerySchema(BaseModel):
    skills: str
    generated_query: str

class GPTResponseInterestsQuerySchema(BaseModel):
    interests: str
    generated_query: str


# API Response Schemas

# GPT SDG relevance explanation
class PublicationSDGAnalysisSchema(BaseModel):
    publication_id: int
    title: str
    abstract: str
    relevance: str
    reasoning: str

    class Config:
        from_attributes = True

# Single Publication Summary Schema
class PublicationSummarySchema(BaseModel):
    publication_id: int
    summary: str

    class Config:
        from_attributes = True  # Enables ORM-style model validation

# Summary for multiple publications
class PublicationsCollectiveSummarySchema(BaseModel):
    publication_ids: List[int]
    summary: str
    keywords: List[str]

class Config:
        from_attributes = True  # Enables ORM-style model validation

# Keywords for a Single Publication Schema
class PublicationKeywordsSchema(BaseModel):
    publication_id: int
    keywords: List[str]

    class Config:
        from_attributes = True


class UserEnrichedSkillsDescriptionSchema(BaseModel):
    input_skills: str
    enriched_description: str

    class Config:
        from_attributes = True

class UserEnrichedInterestsDescriptionSchema(BaseModel):
    input_interests: str
    enriched_description: str

    class Config:
        from_attributes = True

from typing import List

from pydantic import BaseModel

from enums import SDGType


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

class GPTResponseCommentSummarySchema(BaseModel):
    summary: str

class GPTResponseSkillsQuerySchema(BaseModel):
    skills: str
    generated_query: str

class GPTResponseInterestsQuerySchema(BaseModel):
    interests: str
    generated_query: str

class GPTResponseAnnotationScoreSchema(BaseModel):
    relevance: float
    depth: float
    correctness: float
    creativity: float
    reasoning: str


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

# Summary for multiple SDG User Labels
class SDGUserLabelsCommentSummarySchema(BaseModel):
    user_labels_ids: List[int]
    summary: str

class Config:
        from_attributes = True  # Enables ORM-style model validation


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

class SDGPredictionSchema(BaseModel):
    input: str
    proposed_sdg_id: int
    reasoning: str

    class Config:
        from_attributes = True


class AnnotationEvaluationSchema(BaseModel):
    passage: str
    annotation: str
    sdg_label: SDGType  # Use SDGType enum
    relevance: float
    depth: float
    correctness: float
    creativity: float
    reasoning: str
    llm_score: float
    semantic_score: float
    combined_score: float

    class Config:
        from_attributes = True

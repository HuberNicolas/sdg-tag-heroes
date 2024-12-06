from pydantic import BaseModel, Field
from typing import List

class SDGSeedWords(BaseModel):
    sdg_1: List[str] = Field(
        default=["poverty", "inequality", "income", "hunger", "housing",
                 "employment", "nutrition", "security", "aid", "vulnerability"],
        description="Seed words for SDG 1: No Poverty"
    )
    sdg_2: List[str] = Field(
        default=["hunger", "nutrition", "food", "agriculture", "sustainability",
                 "farming", "crops", "resilience", "livelihoods", "harvest"],
        description="Seed words for SDG 2: Zero Hunger"
    )
    sdg_3: List[str] = Field(
        default=["health", "wellness", "vaccination", "disease", "medicine",
                 "hospitals", "hygiene", "epidemics", "mental_health", "sanitation"],
        description="Seed words for SDG 3: Good Health and Well-Being"
    )
    sdg_4: List[str] = Field(
        default=["education", "literacy", "school", "teachers", "learning",
                 "access", "skills", "knowledge", "students", "quality"],
        description="Seed words for SDG 4: Quality Education"
    )
    sdg_5: List[str] = Field(
        default=["gender", "equality", "empowerment", "rights", "inclusion",
                 "discrimination", "education", "leadership", "violence", "justice"],
        description="Seed words for SDG 5: Gender Equality"
    )
    sdg_6: List[str] = Field(
        default=["water", "sanitation", "hygiene", "cleanliness", "access",
                 "sustainability", "waste", "pollution", "health", "safety"],
        description="Seed words for SDG 6: Clean Water and Sanitation"
    )
    sdg_7: List[str] = Field(
        default=["energy", "renewables", "electricity", "sustainability", "efficiency",
                 "access", "clean_energy", "solar", "wind", "power"],
        description="Seed words for SDG 7: Affordable and Clean Energy"
    )
    sdg_8: List[str] = Field(
        default=["employment", "growth", "economy", "jobs", "productivity",
                 "innovation", "sustainability", "business", "rights", "investment"],
        description="Seed words for SDG 8: Decent Work and Economic Growth"
    )
    sdg_9: List[str] = Field(
        default=["infrastructure", "innovation", "technology", "sustainability",
                 "industry", "development", "research", "transportation", "engineering", "growth"],
        description="Seed words for SDG 9: Industry, Innovation and Infrastructure"
    )
    sdg_10: List[str] = Field(
        default=["inequality", "rights", "equity", "discrimination", "justice",
                 "inclusion", "access", "poverty", "migration", "policy"],
        description="Seed words for SDG 10: Reduced Inequalities"
    )
    sdg_11: List[str] = Field(
        default=["sustainability", "urban", "infrastructure", "housing", "transport",
                 "communities", "resilience", "planning", "cleanliness", "safety"],
        description="Seed words for SDG 11: Sustainable Cities and Communities"
    )
    sdg_12: List[str] = Field(
        default=["consumption", "production", "sustainability", "resources", "waste",
                 "efficiency", "recycling", "energy", "pollution", "climate"],
        description="Seed words for SDG 12: Responsible Consumption and Production"
    )
    sdg_13: List[str] = Field(
        default=["climate", "action", "resilience", "emissions", "sustainability",
                 "adaptation", "mitigation", "policies", "energy", "conservation"],
        description="Seed words for SDG 13: Climate Action"
    )
    sdg_14: List[str] = Field(
        default=["oceans", "marine", "biodiversity", "fishing", "pollution",
                 "conservation", "sustainability", "ecosystems", "resources", "habitats"],
        description="Seed words for SDG 14: Life Below Water"
    )
    sdg_15: List[str] = Field(
        default=["biodiversity", "forests", "ecosystems", "wildlife", "conservation",
                 "sustainability", "deforestation", "habitats", "land_use", "restoration"],
        description="Seed words for SDG 15: Life on Land"
    )
    sdg_16: List[str] = Field(
        default=["justice", "peace", "institutions", "governance", "rights",
                 "transparency", "corruption", "equality", "violence", "policy"],
        description="Seed words for SDG 16: Peace, Justice, and Strong Institutions"
    )
    sdg_17: List[str] = Field(
        default=["partnerships", "cooperation", "collaboration", "finance", "development",
                 "innovation", "policy", "investment", "resources", "goals"],
        description="Seed words for SDG 17: Partnerships for the Goals"
    )

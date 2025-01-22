from typing import List
from pydantic import BaseModel

class UserProfileSkillsRequest(BaseModel):
    skills: str

    class Config:
        from_attributes = True

class UserProfileInterestsRequest(BaseModel):
    interests: str

    class Config:
        from_attributes = True

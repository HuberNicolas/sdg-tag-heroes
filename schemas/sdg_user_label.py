from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel


class SDGUserLabelSchemaBase(BaseModel):
    label_id: int
    user_id: int
    publication_id: int
    proposed_label: Optional[int]
    voted_label: int
    abstract_section: Optional[str]
    comment: Optional[str]
    annotations: List[Union["AnnotationSchemaBase", "AnnotationSchemaFull"]]
    votes: List[Union["VoteSchemaBase", "VoteSchemaFull"]]
    label_decisions: List[Union["SDGLabelDecisionSchemaBase", "SDGLabelDecisionSchemaFull"]]

    model_config = {
        "from_attributes": True
    }


class SDGUserLabelSchemaFull(SDGUserLabelSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# Not directly derived from models
# Todo: Generate TS type
class SDGLabelDistribution(BaseModel):
    """Represents the distribution of SDG labels."""
    sdg_label: int  # SDG label (1-17, 18 for non-relevant)
    count: int      # Number of occurrences
    user_ids: List[int]

class UserVotingDetails(BaseModel):
    """Represents voting details for a specific user."""
    user_id: int
    voted_labels: List[int]  # List of SDG labels voted by the user

class SDGUserLabelStatisticsSchema(BaseModel):
    """Represents the statistics for SDG labels and user voting, including full entities."""
    label_distribution: List[SDGLabelDistribution]  # Distribution of latest votes
    total_label_distribution: List[SDGLabelDistribution]  # Distribution of all votes
    user_voting_details: List[UserVotingDetails]    # Voting details per user
    sdg_user_labels: List["SDGUserLabelSchemaFull"]   # Full SDGUserLabel entities

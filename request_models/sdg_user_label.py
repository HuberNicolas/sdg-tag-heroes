from typing import Optional

from pydantic import BaseModel


class UserLabelRequest(BaseModel):
    """
    Request model for creating or linking an SDGUserLabel.
    """
    user_id: int  # The user creating the label
    voted_label: int  # The SDG label voted by the user
    abstract_section: Optional[str] = ""  # Optional abstract section
    comment: Optional[str] = ""  # Optional comment
    decision_id: Optional[int] = None  # Link to an existing decision (optional)
    publication_id: Optional[int] = None  # Link to a publication (optional)
    decision_type: Optional[str] = "CONSENSUS_MAJORITY"  # Default decision type

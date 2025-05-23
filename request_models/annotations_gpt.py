from typing import Optional

from pydantic import BaseModel

from enums.enums import SDGType

class AnnotationCreateRequest(BaseModel):
    """
    Request model for creating an annotation.
    """
    user_id: int  # ID of the user creating the annotation
    passage: str  # The passage being annotated
    sdg_user_label_id: Optional[int] = None  # Optional link to SDGUserLabel
    decision_id: Optional[int] = None  # Optional link to an SDGLabelDecision
    labeler_score: float  # Score assigned by the user
    comment: Optional[str] = ""  # Optional comment

    class Config:
        from_attributes = True

class AnnotationEvaluationRequest(BaseModel):
    passage: str
    annotation: str
    sdg_label: SDGType

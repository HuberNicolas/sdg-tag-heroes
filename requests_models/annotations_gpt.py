from pydantic import BaseModel
from enums.enums import SDGType

class AnnotationEvaluationRequest(BaseModel):
    passage: str
    annotation: str
    sdg_label: SDGType

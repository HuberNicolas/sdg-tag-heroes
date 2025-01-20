from datetime import datetime
from pydantic import BaseModel

class SDGLabelSummarySchemaBase(BaseModel):
    sdg_label_summary_id: int
    publication_id: int
    history_id: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGLabelSummarySchemaFull(SDGLabelSummarySchemaBase):
    sdg1: int
    sdg2: int
    sdg3: int
    sdg4: int
    sdg5: int
    sdg6: int
    sdg7: int
    sdg8: int
    sdg9: int
    sdg10: int
    sdg11: int
    sdg12: int
    sdg13: int
    sdg14: int
    sdg15: int
    sdg16: int
    sdg17: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

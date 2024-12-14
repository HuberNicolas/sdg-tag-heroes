from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from settings.enums import SDGEnum

class SDGXPBankHistorySchemaCreate(BaseModel):
    sdg: SDGEnum
    increment: float
    reason: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGXPBankHistorySchemaFull(SDGXPBankHistorySchemaCreate):
    history_id: int
    xp_bank_id: int

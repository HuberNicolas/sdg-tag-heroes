from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from enums.enums import SDGType


class SDGXPBankHistorySchemaBase(BaseModel):
    history_id: int
    xp_bank_id: int
    sdg: SDGType
    increment: float
    reason: Optional[str]
    is_shown: Optional[bool] = False
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }


class SDGXPBankHistorySchemaFull(SDGXPBankHistorySchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Not directly derived from models
# Todo: Generate TS type
class NoSDGXPBankHistorySchemaBase(BaseModel):
    message: str = "No bank history found for the user."
    increment: float = 0.0
    reason: Optional[str] = "No updates available."

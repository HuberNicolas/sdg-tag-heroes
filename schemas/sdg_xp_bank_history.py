from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from settings.enums import SDGEnum

class SDGXPBankHistorySchemaCreate(BaseModel):
    sdg: SDGEnum
    increment: float
    reason: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True


class SDGXPBankHistorySchemaFull(SDGXPBankHistorySchemaCreate):
    history_id: int
    xp_bank_id: int

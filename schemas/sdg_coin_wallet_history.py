from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SDGCoinWalletHistorySchemaCreate(BaseModel):
    increment: float
    reason: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        orm_mode = True


class SDGCoinWalletHistorySchemaFull(SDGCoinWalletHistorySchemaCreate):
    history_id: int
    wallet_id: int

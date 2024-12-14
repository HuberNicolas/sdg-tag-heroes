from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SDGCoinWalletHistorySchemaCreate(BaseModel):
    increment: float
    reason: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGCoinWalletHistorySchemaFull(SDGCoinWalletHistorySchemaCreate):
    history_id: int
    wallet_id: int

from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class SDGCoinWalletHistorySchemaBase(BaseModel):
    history_id: int
    wallet_id: int
    increment: float
    reason: Optional[str]
    is_shown: Optional[bool] = False
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }


class SDGCoinWalletHistorySchemaFull(SDGCoinWalletHistorySchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

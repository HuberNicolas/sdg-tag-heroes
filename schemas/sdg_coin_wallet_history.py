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

# Not directly derived from models
# Todo: Generate TS type
class NoSDGCoinWalletHistorySchemaBase(BaseModel):
    message: str = "No wallet history found for the user."
    increment: float = 0.0
    reason: Optional[str] = "No updates available."

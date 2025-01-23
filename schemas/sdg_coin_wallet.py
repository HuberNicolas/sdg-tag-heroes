from datetime import datetime
from typing import List, Union

from pydantic import BaseModel


class SDGCoinWalletSchemaBase(BaseModel):
    sdg_coin_wallet_id: int
    user_id: int
    total_coins: float
    histories: List[Union["SDGCoinWalletHistorySchemaBase", "SDGCoinWalletHistorySchemaFull"]]

    model_config = {
        "from_attributes": True
    }


class SDGCoinWalletSchemaFull(SDGCoinWalletSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from datetime import datetime

from pydantic import BaseModel

class SDGCoinWalletSchemaBase(BaseModel):
    sdg_coin_wallet_id: int
    user_id: int

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }


class SDGCoinWalletSchemaFull(SDGCoinWalletSchemaBase):
    total_coins: float
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Enables ORM-style model validation
    }

from datetime import datetime

from pydantic import BaseModel

class SDGCoinWalletSchemaBase(BaseModel):
    sdg_coin_wallet_id: int
    user_id: int

    class Config:
        orm_mode = True


class SDGCoinWalletSchemaFull(SDGCoinWalletSchemaBase):
    total_coins: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

from datetime import datetime

from pydantic import BaseModel

class SDGXPBankSchemaBase(BaseModel):
    sdg_xp_bank_id: int
    user_id: int

    class Config:
        orm_mode = True

class SDGXPBankSchemaFull(SDGXPBankSchemaBase):
    total_xp: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

from pydantic import BaseModel
from datetime import datetime

class SDGXPBankSchemaBase(BaseModel):
    sdg_xp_bank_id: int
    user_id: int

    class Config:
        orm_mode = True


class SDGXPBankSchemaFull(SDGXPBankSchemaBase):
    total_xp: float
    sdg_1_xp: float
    sdg_2_xp: float
    sdg_3_xp: float
    sdg_4_xp: float
    sdg_5_xp: float
    sdg_6_xp: float
    sdg_7_xp: float
    sdg_8_xp: float
    sdg_9_xp: float
    sdg_10_xp: float
    sdg_11_xp: float
    sdg_12_xp: float
    sdg_13_xp: float
    sdg_14_xp: float
    sdg_15_xp: float
    sdg_16_xp: float
    sdg_17_xp: float
    created_at: datetime
    updated_at: datetime

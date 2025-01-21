from datetime import datetime
from pydantic import BaseModel
from typing import List, Union

from schemas import SDGXPBankHistorySchemaBase, SDGXPBankHistorySchemaFull

class SDGXPBankSchemaBase(BaseModel):
    sdg_xp_bank_id: int
    user_id: int
    total_xp: float
    sdg1_xp: float
    sdg2_xp: float
    sdg3_xp: float
    sdg4_xp: float
    sdg5_xp: float
    sdg6_xp: float
    sdg7_xp: float
    sdg8_xp: float
    sdg9_xp: float
    sdg10_xp: float
    sdg11_xp: float
    sdg12_xp: float
    sdg13_xp: float
    sdg14_xp: float
    sdg15_xp: float
    sdg16_xp: float
    sdg17_xp: float
    histories: List[Union[SDGXPBankHistorySchemaBase, SDGXPBankHistorySchemaFull]]

    model_config = {
        "from_attributes": True
    }


class SDGXPBankSchemaFull(SDGXPBankSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

from pydantic import BaseModel

from enums.enums import SDGType


class BankIncrementRequest(BaseModel):
    increment: float
    sdg: SDGType
    reason: str

    class Config:
        from_attributes = True

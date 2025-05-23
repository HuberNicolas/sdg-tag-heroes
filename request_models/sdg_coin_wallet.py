from pydantic import BaseModel

class WalletIncrementRequest(BaseModel):
    increment: float
    reason: str

    class Config:
        from_attributes = True

from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

    class Config:
        # Ensure that attribute names match the model's variable names
        from_attributes = True

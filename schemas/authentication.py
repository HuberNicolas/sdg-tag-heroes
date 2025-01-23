from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from settings.settings import TimeZoneSettings

time_zone_settings = TimeZoneSettings()

def get_current_time():
    return datetime.now(time_zone_settings.ZURICH_TZ)

# Won't be sent
class TokenDataSchemaBase(BaseModel):
    user_id: int
    email: str
    roles: List[str]  # Expecting a list of roles

    model_config = {
        "from_attributes": True
    }

class TokenDataSchemaFull(TokenDataSchemaBase):

    model_config = {
        "from_attributes": True
    }

# Send user details
class UserDataSchemaBase(BaseModel):
    user_id: int
    email: str
    roles: List[str]  # Expecting a list of roles

    model_config = {
        "from_attributes": True
    }

class UserDataSchemaFull(UserDataSchemaBase):
    login_at: Optional[datetime] = Field(default_factory=get_current_time)

    model_config = {
        "from_attributes": True
    }

# Send back access token for user
class LoginSchemaBase(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "from_attributes": True
    }

class LoginSchemaFull(LoginSchemaBase):
    login_at: Optional[datetime] = Field(default_factory=get_current_time)

    model_config = {
        "from_attributes": True
    }





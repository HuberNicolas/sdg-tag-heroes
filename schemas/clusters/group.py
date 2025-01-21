from datetime import datetime
from typing import List, Union
from pydantic import BaseModel


class ClusterGroupSchemaBase(BaseModel):
    id: int
    name: str
    cluster_levels: List[Union["ClusterLevelSchemaBase", "ClusterLevelSchemaFull"]]

    model_config = {
        "from_attributes": True
    }

class ClusterGroupSchemaFull(ClusterGroupSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

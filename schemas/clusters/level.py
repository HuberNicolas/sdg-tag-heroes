from datetime import datetime
from typing import List, Union
from pydantic import BaseModel

from schemas.clusters.topic import ClusterTopicSchemaBase, ClusterTopicSchemaFull

class ClusterLevelSchemaBase(BaseModel):
    id: int
    cluster_group_id: int
    level_number: int
    cluster_topics: List[Union["ClusterTopicSchemaBase", ClusterTopicSchemaFull]]

    model_config = {
        "from_attributes": True
    }

class ClusterLevelSchemaFull(ClusterLevelSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

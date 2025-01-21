from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel

from schemas.clusters.publication_cluster import PublicationClusterSchemaBase, PublicationClusterSchemaFull

class ClusterTopicSchemaBase(BaseModel):
    topic_id: int
    level_id: int
    cluster_id_str: str
    size: float
    center_x: float
    center_y: float
    name: str
    topic_name: str
    publications: List[Union[PublicationClusterSchemaBase, PublicationClusterSchemaFull]]

    model_config = {
        "from_attributes": True
    }

class ClusterTopicSchemaFull(ClusterTopicSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

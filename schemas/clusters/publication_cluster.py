from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PublicationClusterSchemaBase(BaseModel):
    publication_cluster_id: int
    publication_id: int
    cluster_id: int
    cluster_id_string: str
    sdg: Optional[int]
    level: Optional[int]
    topic: Optional[int]

    model_config = {
        "from_attributes": True
    }

class PublicationClusterSchemaFull(PublicationClusterSchemaBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

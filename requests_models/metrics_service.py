from typing import Optional

from pydantic import BaseModel


class MetricsRequestSchema(BaseModel):
    publication_id: Optional[int] = None
    metric_type: Optional[str] = None
    order: Optional[str] = None
    top_n: Optional[int] = None

from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime

class MetricsRequestSchema(BaseModel):
    publication_id: Optional[int] = None
    metric_type: Optional[str] = None
    order: Optional[str] = None
    top_n: Optional[int] = None

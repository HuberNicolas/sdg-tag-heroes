from typing import List, Optional

from pydantic import BaseModel


class PublicationSimilarityQueryRequest(BaseModel):
    user_query: str
    publication_ids: Optional[List[int]] = None

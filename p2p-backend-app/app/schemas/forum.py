from pydantic import BaseModel
from typing import List, Optional


class ForumPostCreate(BaseModel):
    title: str
    content: str
    category_id: str
    tags: Optional[List[str]] = []



from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Annotated

from app.core.input_validation import check_safe_text, check_safe_tag


class ForumPostCreate(BaseModel):
    title: Annotated[str, Field(min_length=8, max_length=150)]
    content: Annotated[str, Field(min_length=20, max_length=5000)]
    category_id: Annotated[str, Field(min_length=1)]
    tags: Optional[Annotated[List[str], Field(max_length=5)]] = []

    @field_validator('title', 'content', 'category_id')
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            for item in v:
                check_safe_tag(item)
        return v



from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Annotated

from app.core.input_validation import check_safe_text, check_safe_tag, check_safe_title

ALLOWED_FORUM_CATEGORIES = {
    "Automation",
    "Quality Management",
    "Artificial Intelligence",
    "Maintenance",
    "Lean Manufacturing",
    "Supply Chain Management",
    "Digital Transformation",
    "IoT & Sensors",
    "Robotics",
    "Cybersecurity",
    "Energy Efficiency",
    "Sustainability",
    "Safety & Compliance",
    "Training & Development",
    "Cost Optimization",
    "Inventory Management",
    "Production Planning",
    "Machine Learning",
    "Data Analytics",
    "ERP Systems",
    "Cloud Computing",
    "3D Printing",
    "Packaging",
    "Logistics",
    "Procurement",
    "Vendor Management",
    "Regulatory Compliance",
    "Continuous Improvement",
    "Workflow Optimization",
    "Equipment Management",
    "Facility Management",
    "Human Resources",
    "Financial Management",
    "Research & Development",
    "Customer Service",
    "General Discussion",
    "Technical Support",
    "Best Practices",
    "Announcements",
    "Feature Requests",
}

class AttachmentModel(BaseModel):
    filename: Annotated[str, Field(max_length=255)]
    url: Annotated[str, Field(max_length=1000)]
    mime_type: Annotated[str, Field(max_length=100)]
    size: Annotated[int, Field(ge=0)]
    source: Optional[Annotated[str, Field(max_length=100)]] = None

    @field_validator('filename', 'mime_type', 'source')
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('url')
    @classmethod
    def validate_safe_urls(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v


class ForumPostCreate(BaseModel):
    title: Annotated[str, Field(min_length=8, max_length=150)]
    content: Annotated[str, Field(min_length=20, max_length=5000)]
    category_id: Annotated[str, Field(min_length=1)]
    tags: Optional[Annotated[List[str], Field(max_length=5)]] = []

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        return check_safe_title(v)

    @field_validator('category_id')
    @classmethod
    def validate_category(cls, v):
        v_safe = check_safe_text(v)
        # Handle both slug-like and human-readable names
        norm = " ".join(w.capitalize() for w in str(v_safe).replace("-", " ").strip().lower().split())
        if norm not in ALLOWED_FORUM_CATEGORIES and v_safe not in ALLOWED_FORUM_CATEGORIES:
            allowed_str = ", ".join(sorted(ALLOWED_FORUM_CATEGORIES))
            raise ValueError(f"Category not allowed. Allowed categories: {allowed_str}")
        return v_safe

    @field_validator('content')
    @classmethod
    def validate_safe_content(cls, v):
        return check_safe_text(v, allow_urls=True)

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v is not None:
            for item in v:
                check_safe_tag(item)
        return v



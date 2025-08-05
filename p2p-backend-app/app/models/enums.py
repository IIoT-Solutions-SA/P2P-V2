"""Enum definitions for models."""

from enum import Enum


class UserRole(str, Enum):
    """User roles within an organization."""
    ADMIN = "admin"
    MEMBER = "member"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"  # Waiting for email verification
    SUSPENDED = "suspended"


class OrganizationStatus(str, Enum):
    """Organization account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class IndustryType(str, Enum):
    """Industry types for organizations and use cases."""
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    TECHNOLOGY = "technology"
    EDUCATION = "education"
    CONSTRUCTION = "construction"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    OTHER = "other"


class TechnologyCategory(str, Enum):
    """Technology categories for use cases."""
    AI_ML = "ai_ml"
    IOT = "iot"
    BLOCKCHAIN = "blockchain"
    CLOUD_COMPUTING = "cloud_computing"
    CYBERSECURITY = "cybersecurity"
    DATA_ANALYTICS = "data_analytics"
    AUTOMATION = "automation"
    AR_VR = "ar_vr"
    ROBOTICS = "robotics"
    OTHER = "other"


class ForumCategory(str, Enum):
    """Forum topic categories."""
    GENERAL_DISCUSSION = "general_discussion"
    TECHNICAL_HELP = "technical_help"
    USE_CASE_DISCUSSION = "use_case_discussion"
    BEST_PRACTICES = "best_practices"
    INDUSTRY_NEWS = "industry_news"
    EVENTS_MEETUPS = "events_meetups"
    PARTNERSHIPS = "partnerships"
    FEEDBACK_SUGGESTIONS = "feedback_suggestions"


class MessageStatus(str, Enum):
    """Message read status."""
    UNREAD = "unread"
    READ = "read"


class NotificationType(str, Enum):
    """Types of notifications."""
    FORUM_REPLY = "forum_reply"
    FORUM_MENTION = "forum_mention"
    PRIVATE_MESSAGE = "private_message"
    USE_CASE_COMMENT = "use_case_comment"
    USE_CASE_APPROVED = "use_case_approved"
    USER_JOINED = "user_joined"
    SYSTEM = "system"
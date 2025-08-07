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


class InvitationStatus(str, Enum):
    """Status of user invitations."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


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


class ForumCategoryType(str, Enum):
    """Forum category types based on frontend implementation."""
    AUTOMATION = "automation"
    QUALITY_MANAGEMENT = "quality_management"  
    MAINTENANCE = "maintenance"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    IOT = "iot"
    GENERAL = "general"


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
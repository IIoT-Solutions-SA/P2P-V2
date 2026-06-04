import re
from typing import Set, List, Tuple, Pattern

# ── Pattern → friendly error message mapping ──
# Ordered so more specific patterns match first
PATTERN_RULES: List[Tuple[Pattern, str]] = [
    (re.compile(r"<\s*/\s*script\s*>", re.IGNORECASE),         "HTML closing script tags are not allowed"),
    (re.compile(r"<\s*script", re.IGNORECASE),                  "HTML script tags are not allowed"),
    (re.compile(r"javascript\s*:", re.IGNORECASE),              "JavaScript protocol in URLs is not allowed"),
    (re.compile(r"on(error|load|click|mouseover|keydown|submit|focus|blur|change)\s*=", re.IGNORECASE),
                                                                 "HTML event handlers (e.g. onclick, onerror) are not allowed"),
    (re.compile(r"\.\.\\\\"),                                   r"Path traversal sequences (..\\) are not allowed"),
    (re.compile(r"\.\./"),                                      "Path traversal sequences (../) are not allowed"),
    (re.compile(r"/etc/passwd"),                                "References to system files are not allowed"),
    (re.compile(r"oastify\.com", re.IGNORECASE),                "External callback domains are not allowed"),
    (re.compile(r"<!DOCTYPE", re.IGNORECASE),                   "XML/HTML doctype declarations are not allowed"),
    (re.compile(r"<\w+:include", re.IGNORECASE),                "XML entity includes are not allowed"),
    (re.compile(r"xsi:schemaLocation", re.IGNORECASE),          "XML schema location references are not allowed"),
    (re.compile(r"<!--#\w+", re.IGNORECASE),                    "Server-side include directives are not allowed"),
    (re.compile(r"objectClass\s*=", re.IGNORECASE),             "LDAP query patterns are not allowed"),
    (re.compile(r"[\x00]"),                                     "Null characters are not allowed"),
]


def check_safe_text(value: str) -> str:
    """Reject security payloads with a specific, user-friendly error message."""
    if not isinstance(value, str):
        return value

    for pattern, message in PATTERN_RULES:
        if pattern.search(value):
            raise ValueError(message)

    return value


def check_safe_tag(value: str) -> str:
    """Stricter validation for tags — alphanumeric, spaces, hyphens, Arabic chars only."""
    if not isinstance(value, str):
        return value

    check_safe_text(value)

    if len(value) < 2 or len(value) > 30:
        raise ValueError("Each tag must be between 2 and 30 characters")

    if not re.match(r"^[\w\s\-\u0600-\u06FF]+$", value):
        raise ValueError("Tags can only contain letters, numbers, spaces, and hyphens")

    return value


ALLOWED_USECASE_CATEGORIES: Set[str] = {
    "Quality Control",
    "Predictive Maintenance",
    "Factory Automation",
    "Artificial Intelligence",
    "Sustainability",
    "Process Optimization",
    "Supply Chain",
    "Innovation & R&D",
    "Training & Safety",
    "Energy Efficiency",
}

ALLOWED_USECASE_CATEGORIES_STR: str = (
    "Quality Control, Predictive Maintenance, Factory Automation, "
    "Artificial Intelligence, Sustainability, Process Optimization, "
    "Supply Chain, Innovation & R&D, Training & Safety, Energy Efficiency"
)

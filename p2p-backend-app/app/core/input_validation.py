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
    (re.compile(r"(.)\1{4,}"),                                  "Too many repeated characters are not allowed"),
    (re.compile(r"[^\w\s\.\-,\n:/]{4,}"),                       "Excessive consecutive special characters are not allowed"),
    (re.compile(r"(?i)[bcdfghjklmnpqrstvwxz]{6,}"),             "Too many consecutive consonants are not allowed"),
]

URL_PATTERN = re.compile(r"https?://|www\.", re.IGNORECASE)

def check_safe_text(value: str, allow_urls: bool = False, allow_html: bool = False) -> str:
    """Reject security payloads with a specific, user-friendly error message."""
    if not isinstance(value, str):
        return value

    value = value.strip()
    if not value:
        return value

    # Normalize repeated whitespace
    value = re.sub(r'\s+', ' ', value)

    # Require minimum number of Arabic/English letters or digits
    # \w covers a-z, A-Z, 0-9, and _. \u0600-\u06FF covers Arabic.
    valid_chars = len(re.findall(r'[\w\u0600-\u06FF]', value))
    # Only enforce if string is not empty
    if len(value) > 0 and valid_chars < 3:
        raise ValueError("Input must contain at least 3 valid letters or numbers")

    # Reject if symbol ratio is too high (e.g. > 50% for strings longer than 10)
    if len(value) > 10:
        symbol_chars = len(re.findall(r'[^\w\s\u0600-\u06FF]', value))
        if symbol_chars / len(value) > 0.5:
            raise ValueError("Input contains too many symbols")

    if not allow_urls and URL_PATTERN.search(value):
        raise ValueError("URLs and links are not allowed in this field")

    for pattern, message in PATTERN_RULES:
        if pattern.search(value):
            raise ValueError(message)

    if not allow_html:
        if re.search(r'<\/?[\w\s="\'\-:]+>', value):
            raise ValueError("HTML tags are not allowed in this field")

    return value


def check_safe_title(value: str) -> str:
    """Additional checks specifically for titles."""
    if not isinstance(value, str):
        return value
    
    value = check_safe_text(value, allow_urls=False)
    
    # Check total number of special characters (excluding dot, comma, hyphen, space)
    special_chars = re.findall(r'[^\w\s\.\-,]', value)
    if len(special_chars) > 3:
        raise ValueError("Too many special characters are not allowed in titles")
        
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

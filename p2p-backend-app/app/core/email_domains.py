from typing import Iterable


def get_email_domain(email: str | None) -> str:
    if not email or "@" not in email:
        return ""
    return email.split("@")[-1].strip().lower()


def is_blocked_domain(domain: str, blocked_domains: Iterable[str]) -> bool:
    normalized_blocked = {d.strip().lower() for d in blocked_domains if d.strip()}
    return domain.strip().lower() in normalized_blocked

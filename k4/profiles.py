"""Business firewall profiles for K4."""

from k4.config import FIREWALL_PROFILES
from k4.types import FirewallProfile


def get_firewall_profile(name: str | None) -> FirewallProfile:
    if not name:
        return FIREWALL_PROFILES["coding"]
    return FIREWALL_PROFILES.get(name, FIREWALL_PROFILES["coding"])


def select_firewall_profile(requirement: str, requested: str | None = None) -> FirewallProfile:
    if requested:
        return get_firewall_profile(requested)

    text = requirement.lower()
    if any(word in text for word in ("research", "search")):
        return FIREWALL_PROFILES["research"]
    if any(word in text for word in ("database", "sql", "mysql")):
        return FIREWALL_PROFILES["database"]
    return FIREWALL_PROFILES["coding"]

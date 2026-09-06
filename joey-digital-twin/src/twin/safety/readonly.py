"""Read-only capability gate for v0.1.

AGENTS.md section 3. Future permissions are ARCHITECTED (named, typed, gated)
but NOT ENABLED. Every capability below is False and the set is frozen.

Any change flipping one of these to True must be rejected in review, and
tests/test_readonly.py will fail.
"""

from __future__ import annotations

from dataclasses import dataclass


class ReadOnlyViolation(RuntimeError):
    """An external-write action was attempted under v0.1 read-only authority."""


# Named future permissions. Present so the permission surface is explicit and
# reviewable, not so it can be switched on.
CAPABILITIES: dict[str, bool] = {
    "send_email": False,
    "send_message": False,
    "post_social": False,
    "write_crm": False,
    "delete_data": False,
    "purchase": False,
    "schedule_meeting": False,
    "submit_application": False,
    "contact_prospect": False,
    "financial_transaction": False,
    "external_http_write": False,
    "modify_memory": False,
}

_FROZEN = tuple(sorted(CAPABILITIES))


@dataclass(frozen=True)
class Authority:
    """The authority under which the engine runs. v0.1 is READ_ONLY."""

    level: str = "READ_ONLY"

    def allows(self, capability: str) -> bool:
        if capability not in CAPABILITIES:
            raise ReadOnlyViolation(f"unknown capability {capability!r}")
        return CAPABILITIES[capability] and self.level != "READ_ONLY"


READ_ONLY = Authority()


def require(capability: str, authority: Authority = READ_ONLY) -> None:
    """Gate an external-effect action. In v0.1 this always raises."""
    if not authority.allows(capability):
        raise ReadOnlyViolation(
            f"v0.1 is read-only: {capability!r} is not permitted. "
            "The system recommends; Joey decides and acts. See AGENTS.md section 3."
        )


def assert_read_only() -> None:
    """Verify no capability has been enabled and the surface has not drifted."""
    enabled = sorted(k for k, v in CAPABILITIES.items() if v)
    if enabled:
        raise ReadOnlyViolation(f"external-write capabilities enabled in v0.1: {enabled}")
    if tuple(sorted(CAPABILITIES)) != _FROZEN:
        raise ReadOnlyViolation("capability set changed at runtime")

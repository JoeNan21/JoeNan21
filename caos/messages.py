"""Message generation layer.

Operator rules (CRITICAL):
  - No passive language.
  - No "checking in".
  - Always push YES / NO / NOT NOW.
  - 1-4 lines max.
  - Every action moves the deal forward.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

VENUE = "Sorrento in the Park"
OPERATOR = "Joey"

BANNED_PHRASES = (
    "just checking in",
    "checking in",
    "circling back",
    "touching base",
    "wanted to follow up",
    "hope this finds you well",
    "no rush",
    "whenever you get a chance",
    "let me know if",
)


@dataclass(frozen=True)
class Message:
    kind: str        # FIRST_RESPONSE / FOLLOW_UP / CLOSE / AT_RISK
    subject: str
    body: str

    def render(self) -> str:
        return f"Subject: {self.subject}\n\n{self.body}"


def _first_name(name: str | None) -> str:
    if not name:
        return "there"
    return str(name).strip().split()[0]


def _event_phrase(lead: Mapping) -> str:
    et = (lead.get("event_type") or "").strip().lower() or "event"
    parts = [et]
    if lead.get("guest_count"):
        parts.append(f"for {lead['guest_count']} guests")
    if lead.get("event_date"):
        parts.append(f"on {lead['event_date']}")
    return " ".join(parts)


def first_response(lead: Mapping) -> Message:
    name = _first_name(lead.get("name"))
    body = (
        f"Hi {name} — {OPERATOR} from {VENUE}.\n"
        f"Got your enquiry for a {_event_phrase(lead)}.\n"
        f"I can hold the date for 48 hours. "
        f"Want to lock a 20-min site visit this week — Wed 6pm or Sat 11am?"
    )
    return Message("FIRST_RESPONSE", f"{VENUE} — your {lead.get('event_type') or 'event'}", body)


def follow_up(lead: Mapping) -> Message:
    name = _first_name(lead.get("name"))
    et = (lead.get("event_type") or "event").lower()
    body = (
        f"{name} — straight up: is the {et} still happening?\n"
        f"YES → I'll book the site visit now.\n"
        f"NO → I'll release the date.\n"
        f"NOT NOW → tell me the week you'll decide."
    )
    return Message("FOLLOW_UP", f"{VENUE} — {et} decision", body)


def close_message(lead: Mapping) -> Message:
    name = _first_name(lead.get("name"))
    et = (lead.get("event_type") or "event").lower()
    body = (
        f"{name} — great seeing you at the site.\n"
        f"Quote attached. Date held until end of tomorrow.\n"
        f"Send the deposit and the {et} is locked in. Yes or no by 5pm?"
    )
    return Message("CLOSE", f"{VENUE} — lock in your {et}", body)


def at_risk_message(lead: Mapping) -> Message:
    name = _first_name(lead.get("name"))
    et = (lead.get("event_type") or "event").lower()
    body = (
        f"{name} — last call on the {et}.\n"
        f"I have another enquiry on this date.\n"
        f"YES, NO, or NOT NOW — reply today and the date is yours."
    )
    return Message("AT_RISK", f"{VENUE} — releasing the date", body)


def for_lead(lead: Mapping) -> Message:
    """Pick the right message for the lead's current state."""
    status = (lead.get("status") or "NEW").upper()
    if lead.get("at_risk"):
        return at_risk_message(lead)
    if status in {"VISITED", "PROPOSAL"}:
        return close_message(lead)
    if status in {"CONTACTED", "VISIT BOOKED"}:
        return follow_up(lead)
    return first_response(lead)


def all_for_lead(lead: Mapping) -> dict[str, Message]:
    return {
        "first_response": first_response(lead),
        "follow_up": follow_up(lead),
        "close": close_message(lead),
        "at_risk": at_risk_message(lead),
    }


def lint(message: Message) -> list[str]:
    """Return any operator-rule violations. Empty list = clean."""
    violations: list[str] = []
    body = message.body.strip()

    lines = [ln for ln in body.splitlines() if ln.strip()]
    if len(lines) > 6:  # subject + 4 body lines + headroom
        violations.append(f"too long ({len(lines)} lines)")

    lower = body.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lower:
            violations.append(f"banned passive phrase: '{phrase}'")

    has_question = "?" in body
    has_decision_token = any(token in body for token in ("YES", "NO", "NOT NOW"))
    if not (has_question or has_decision_token):
        violations.append("no direct ask")

    return violations

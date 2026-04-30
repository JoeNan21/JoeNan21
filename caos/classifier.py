"""Classification + priority scoring engine.

Rules:
  HOT  = post-visit, OR (firm date AND guest count)
  WARM = partial info (date OR guest count, but not both)
  COLD = low info (no date, no guest count)

Priority score is a 0-100 integer derived from:
  base from classification, modified by status, recency, guest count, and risk.
The score is used to sort the daily command console.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Mapping

POST_VISIT_STATUSES = {"VISITED", "PROPOSAL"}
ACTIVE_STATUSES = {"NEW", "CONTACTED", "VISIT BOOKED", "VISITED", "PROPOSAL"}
DEAD_STATUSES = {"CLOSED", "LOST"}


@dataclass(frozen=True)
class Classification:
    label: str          # HOT / WARM / COLD
    score: int          # 0-100
    reasons: tuple[str, ...]


def _has(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (int, float)):
        return value > 0
    return True


def classify(lead: Mapping) -> Classification:
    status = (lead.get("status") or "NEW").upper()
    if status in DEAD_STATUSES:
        return Classification(label="COLD", score=0, reasons=(f"status={status}",))

    has_date = _has(lead.get("event_date"))
    has_guests = _has(lead.get("guest_count"))
    post_visit = status in POST_VISIT_STATUSES or _has(lead.get("visit_completed_at"))

    reasons: list[str] = []
    if post_visit:
        label = "HOT"
        reasons.append("post-visit")
    elif has_date and has_guests:
        label = "HOT"
        reasons.append("date+guests")
    elif has_date or has_guests:
        label = "WARM"
        reasons.append("partial info")
    else:
        label = "COLD"
        reasons.append("low info")

    score = _priority(lead, label, post_visit, has_date, has_guests, reasons)
    return Classification(label=label, score=score, reasons=tuple(reasons))


def _priority(
    lead: Mapping,
    label: str,
    post_visit: bool,
    has_date: bool,
    has_guests: bool,
    reasons: list[str],
) -> int:
    base = {"HOT": 60, "WARM": 35, "COLD": 15}[label]
    score = base

    status = (lead.get("status") or "NEW").upper()

    # Post-visit gets MAX priority — operator must close in 24h.
    if post_visit:
        return 100

    if status == "VISIT BOOKED":
        score += 15
        reasons.append("visit booked")

    # Guest-count revenue weighting (capped).
    guests = lead.get("guest_count") or 0
    if guests:
        score += min(int(guests) // 25, 10)
        if guests >= 100:
            reasons.append(f"{guests} guests")

    # Date proximity — closer events convert faster.
    days_to_event = _days_until(lead.get("event_date"))
    if days_to_event is not None:
        if days_to_event <= 30:
            score += 10
            reasons.append(f"{days_to_event}d to event")
        elif days_to_event <= 90:
            score += 5

    # At-risk flag pushes urgency up.
    if lead.get("at_risk"):
        score += 10
        reasons.append("AT RISK")

    # Stale leads decay slightly so fresh ones surface.
    days_since_contact = _days_since(lead.get("last_contact_date"))
    if days_since_contact is not None and days_since_contact > 7 and not lead.get("at_risk"):
        score -= min(days_since_contact - 7, 10)

    return max(0, min(100, score))


def _days_until(date_str) -> int | None:
    d = _parse_date(date_str)
    if d is None:
        return None
    return (d.date() - datetime.utcnow().date()).days


def _days_since(date_str) -> int | None:
    d = _parse_date(date_str)
    if d is None:
        return None
    return (datetime.utcnow().date() - d.date()).days


def _parse_date(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(value)[: len(fmt) + 2], fmt)
        except ValueError:
            continue
    return None


def at_risk_threshold_hours() -> int:
    return 36  # midway between the 24-48h window

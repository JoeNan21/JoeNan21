"""Demo lead set covering every lane of the command console."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from . import leads


def _date(days: int) -> str:
    return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")


DEMO_LEADS = [
    # CLOSE NOW lane (post-visit, 24h timer running)
    {
        "name": "Maria Conti", "contact": "maria@example.com",
        "event_type": "wedding", "event_date": _date(45),
        "guest_count": 140, "source": "instagram", "status": "VISITED",
        "notes": "Loved the garden ceremony space. Wants pricing on bar package.",
    },
    {
        "name": "Dimitri Volkov", "contact": "+61 412 555 010",
        "event_type": "engagement", "event_date": _date(28),
        "guest_count": 80, "source": "referral", "status": "PROPOSAL",
        "notes": "Quote sent. Decision Friday.",
    },

    # HOT lane (date + guests, not yet visited)
    {
        "name": "Priya Singh", "contact": "priya@example.com",
        "event_type": "wedding", "event_date": _date(60),
        "guest_count": 180, "source": "google", "status": "CONTACTED",
        "notes": "Asked for Sat 11am visit slot.",
    },
    {
        "name": "Tom Bryant", "contact": "tom@example.com",
        "event_type": "corporate", "event_date": _date(20),
        "guest_count": 120, "source": "website", "status": "VISIT BOOKED",
        "notes": "Site visit Wed 6pm.",
    },

    # AT RISK lane (force flag via old contact date)
    {
        "name": "Kelly Nguyen", "contact": "kelly@example.com",
        "event_type": "birthday", "event_date": _date(55),
        "guest_count": 60, "source": "facebook", "status": "CONTACTED",
        "notes": "Asked for menu, went quiet.",
    },

    # LOW lane (warm + cold)
    {
        "name": "Sam Patel", "contact": "sam@example.com",
        "event_type": "private event", "event_date": None,
        "guest_count": 40, "source": "walk-in", "status": "NEW",
        "notes": "Wants something in spring, no firm date.",
    },
    {
        "name": "Anonymous enquiry", "contact": "info@example.com",
        "event_type": None, "event_date": None,
        "guest_count": None, "source": "website", "status": "NEW",
        "notes": "Generic enquiry — needs qualifying call.",
    },
]


def load(conn: sqlite3.Connection) -> int:
    # Wipe existing demo data (idempotent reseed).
    conn.execute("DELETE FROM lead_events")
    conn.execute("DELETE FROM leads")

    today = datetime.utcnow().date()

    for spec in DEMO_LEADS:
        lead_id = leads.create(conn, **spec)

        if spec["status"] == "VISITED":
            conn.execute(
                "UPDATE leads SET visit_completed_at = ?, last_contact_date = ? WHERE id = ?",
                ((datetime.utcnow() - timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S"),
                 (today - timedelta(days=1)).strftime("%Y-%m-%d"), lead_id),
            )
        elif spec["status"] == "PROPOSAL":
            conn.execute(
                "UPDATE leads SET visit_completed_at = ?, last_contact_date = ? WHERE id = ?",
                ((datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                 (today - timedelta(days=1)).strftime("%Y-%m-%d"), lead_id),
            )
        elif spec["status"] == "CONTACTED" and spec["name"] == "Kelly Nguyen":
            # Force AT RISK by aging the contact date past the threshold.
            conn.execute(
                "UPDATE leads SET last_contact_date = ? WHERE id = ?",
                ((today - timedelta(days=4)).strftime("%Y-%m-%d"), lead_id),
            )
        elif spec["status"] in {"CONTACTED", "VISIT BOOKED"}:
            conn.execute(
                "UPDATE leads SET last_contact_date = ? WHERE id = ?",
                (today.strftime("%Y-%m-%d"), lead_id),
            )

        leads._recompute(conn, lead_id)

    return len(DEMO_LEADS)

"""Automation triggers.

Triggers run on every CLI invocation that affects state, plus on
`caos sweep` for periodic at-risk detection. They are pure functions of
the lead store — re-running them is safe.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta

from . import db, leads, messages


@dataclass
class TriggerResult:
    name: str
    lead_id: int
    action: str
    suggested_message: str | None = None


def on_new_lead(conn: sqlite3.Connection, lead_id: int) -> TriggerResult:
    lead = leads.get(conn, lead_id)
    if not lead:
        raise ValueError(f"lead {lead_id} not found")
    msg = messages.first_response(lead)
    db.log_event(conn, lead_id, "TRIGGER", "NEW_LEAD")
    return TriggerResult(
        name="NEW_LEAD",
        lead_id=lead_id,
        action=f"classified={lead.get('classification')} score={lead.get('priority_score')}",
        suggested_message=msg.render(),
    )


def on_visit_booked(conn: sqlite3.Connection, lead_id: int) -> TriggerResult:
    leads.set_status(conn, lead_id, "VISIT BOOKED")
    db.log_event(conn, lead_id, "TRIGGER", "VISIT_BOOKED")
    return TriggerResult(
        name="VISIT_BOOKED",
        lead_id=lead_id,
        action="priority increased; visit confirmed",
    )


def on_visit_completed(conn: sqlite3.Connection, lead_id: int) -> TriggerResult:
    leads.set_status(conn, lead_id, "VISITED")
    lead = leads.get(conn, lead_id)
    msg = messages.close_message(lead or {})
    db.log_event(conn, lead_id, "TRIGGER", "VISIT_COMPLETED")
    return TriggerResult(
        name="VISIT_COMPLETED",
        lead_id=lead_id,
        action="priority=MAX (100); 24h close timer started",
        suggested_message=msg.render(),
    )


def sweep_at_risk(conn: sqlite3.Connection) -> list[TriggerResult]:
    """Flag stale leads and emit follow-up messages for them."""
    flagged = leads.sweep_at_risk(conn)
    out: list[TriggerResult] = []
    for lead in flagged:
        msg = messages.at_risk_message(lead)
        db.log_event(conn, lead["id"], "TRIGGER", "AT_RISK")
        out.append(TriggerResult(
            name="AT_RISK",
            lead_id=lead["id"],
            action="flagged AT RISK (no contact in 24-48h+)",
            suggested_message=msg.render(),
        ))
    return out


def overdue_close_timers(conn: sqlite3.Connection) -> list[dict]:
    """Post-visit leads where the 24h close window has expired."""
    cutoff = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        """
        SELECT * FROM leads
        WHERE status = 'VISITED'
          AND visit_completed_at IS NOT NULL
          AND visit_completed_at <= ?
        ORDER BY priority_score DESC
        """,
        (cutoff,),
    ).fetchall()
    return [dict(r) for r in rows]

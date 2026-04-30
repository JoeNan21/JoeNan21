"""Lead CRUD + lifecycle operations.

Every write goes through here so classification + priority stay in sync
with the rest of the system.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from typing import Any, Iterable

from . import db
from .classifier import (
    ACTIVE_STATUSES,
    DEAD_STATUSES,
    POST_VISIT_STATUSES,
    at_risk_threshold_hours,
    classify,
)

VALID_STATUSES = {
    "NEW", "CONTACTED", "VISIT BOOKED", "VISITED", "PROPOSAL", "CLOSED", "LOST",
}

LEAD_FIELDS = [
    "name", "contact", "event_type", "event_date", "guest_count",
    "source", "status", "notes",
]


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def _today() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def _row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


def create(conn: sqlite3.Connection, **fields: Any) -> int:
    name = (fields.get("name") or "").strip()
    if not name:
        raise ValueError("name is required")

    status = (fields.get("status") or "NEW").upper()
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")

    payload = {f: fields.get(f) for f in LEAD_FIELDS}
    payload["status"] = status

    cur = conn.execute(
        f"""
        INSERT INTO leads ({", ".join(LEAD_FIELDS)})
        VALUES ({", ".join("?" for _ in LEAD_FIELDS)})
        """,
        [payload[f] for f in LEAD_FIELDS],
    )
    lead_id = cur.lastrowid
    db.log_event(conn, lead_id, "CREATED", f"source={payload.get('source') or '-'}")
    _recompute(conn, lead_id)
    return lead_id


def get(conn: sqlite3.Connection, lead_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    return _row_to_dict(row) if row else None


def list_all(conn: sqlite3.Connection, include_dead: bool = False) -> list[dict]:
    if include_dead:
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY priority_score DESC, updated_at DESC"
        ).fetchall()
    else:
        placeholders = ",".join("?" for _ in ACTIVE_STATUSES)
        rows = conn.execute(
            f"SELECT * FROM leads WHERE status IN ({placeholders}) "
            "ORDER BY priority_score DESC, updated_at DESC",
            tuple(ACTIVE_STATUSES),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def update(conn: sqlite3.Connection, lead_id: int, **fields: Any) -> dict:
    lead = get(conn, lead_id)
    if not lead:
        raise ValueError(f"lead {lead_id} not found")

    allowed = set(LEAD_FIELDS) | {
        "last_contact_date", "next_action_date", "at_risk", "visit_completed_at",
    }
    sets, vals = [], []
    for k, v in fields.items():
        if k not in allowed:
            continue
        if k == "status":
            v = str(v).upper()
            if v not in VALID_STATUSES:
                raise ValueError(f"invalid status: {v}")
        sets.append(f"{k} = ?")
        vals.append(v)
    if not sets:
        return lead

    sets.append("updated_at = ?")
    vals.append(_now())
    vals.append(lead_id)
    conn.execute(f"UPDATE leads SET {', '.join(sets)} WHERE id = ?", vals)
    db.log_event(conn, lead_id, "UPDATED", ",".join(f"{k}={v}" for k, v in fields.items()))
    _recompute(conn, lead_id)
    return get(conn, lead_id)  # type: ignore[return-value]


def set_status(conn: sqlite3.Connection, lead_id: int, status: str) -> dict:
    status = status.upper()
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")

    extras: dict[str, Any] = {"status": status, "last_contact_date": _today()}
    if status == "VISITED":
        extras["visit_completed_at"] = _now()
        # Schedule the 24h follow-up timer.
        extras["next_action_date"] = (datetime.utcnow() + timedelta(hours=24)).strftime("%Y-%m-%d")
        extras["at_risk"] = 0
    elif status == "VISIT BOOKED":
        extras["at_risk"] = 0
    elif status in DEAD_STATUSES:
        extras["next_action_date"] = None
        extras["at_risk"] = 0
    return update(conn, lead_id, **extras)


def mark_contacted(conn: sqlite3.Connection, lead_id: int, note: str | None = None) -> dict:
    fields = {"last_contact_date": _today(), "at_risk": 0}
    if note:
        existing = get(conn, lead_id)
        prior = (existing or {}).get("notes") or ""
        stamp = datetime.utcnow().strftime("%Y-%m-%d")
        fields["notes"] = (prior + f"\n[{stamp}] {note}").strip()
    return update(conn, lead_id, **fields)


def flag_at_risk(conn: sqlite3.Connection, lead_id: int) -> dict:
    lead = update(conn, lead_id, at_risk=1)
    db.log_event(conn, lead_id, "FLAGGED_AT_RISK")
    return lead


def sweep_at_risk(conn: sqlite3.Connection) -> list[dict]:
    """Flag any active lead with no contact for >= threshold hours."""
    threshold = at_risk_threshold_hours()
    cutoff = (datetime.utcnow() - timedelta(hours=threshold)).strftime("%Y-%m-%d")
    placeholders = ",".join("?" for _ in ACTIVE_STATUSES)
    rows = conn.execute(
        f"""
        SELECT * FROM leads
        WHERE status IN ({placeholders})
          AND at_risk = 0
          AND (
            (last_contact_date IS NOT NULL AND last_contact_date <= ?)
            OR (last_contact_date IS NULL AND date(created_at) <= ?)
          )
        """,
        (*ACTIVE_STATUSES, cutoff, cutoff),
    ).fetchall()

    flagged = []
    for row in rows:
        flagged.append(flag_at_risk(conn, row["id"]))
    return flagged


def _recompute(conn: sqlite3.Connection, lead_id: int) -> None:
    lead = get(conn, lead_id)
    if not lead:
        return
    c = classify(lead)
    conn.execute(
        "UPDATE leads SET classification = ?, priority_score = ?, updated_at = ? WHERE id = ?",
        (c.label, c.score, _now(), lead_id),
    )


def recompute_all(conn: sqlite3.Connection) -> int:
    rows = conn.execute("SELECT id FROM leads").fetchall()
    for r in rows:
        _recompute(conn, r["id"])
    return len(rows)


def filter_by(leads: Iterable[dict], **predicates: Any) -> list[dict]:
    out = []
    for lead in leads:
        if all(lead.get(k) == v for k, v in predicates.items()):
            out.append(lead)
    return out

"""SQLite storage layer for CAOS leads."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DEFAULT_DB_PATH = Path(os.environ.get("CAOS_DB", Path.cwd() / "caos.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT NOT NULL,
    contact              TEXT,
    event_type           TEXT,
    event_date           TEXT,
    guest_count          INTEGER,
    source               TEXT,
    status               TEXT NOT NULL DEFAULT 'NEW',
    classification       TEXT,
    priority_score       INTEGER NOT NULL DEFAULT 0,
    last_contact_date    TEXT,
    next_action_date     TEXT,
    visit_completed_at   TEXT,
    at_risk              INTEGER NOT NULL DEFAULT 0,
    notes                TEXT,
    created_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_leads_status   ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority_score DESC);

CREATE TABLE IF NOT EXISTS lead_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id     INTEGER NOT NULL,
    event_type  TEXT NOT NULL,
    payload     TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(lead_id) REFERENCES leads(id) ON DELETE CASCADE
);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init(db_path: Path | str | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def session(db_path: Path | str | None = None):
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def log_event(conn: sqlite3.Connection, lead_id: int, event_type: str, payload: str = "") -> None:
    conn.execute(
        "INSERT INTO lead_events (lead_id, event_type, payload) VALUES (?, ?, ?)",
        (lead_id, event_type, payload),
    )

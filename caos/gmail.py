"""Optional Gmail integration.

Pulls enquiry emails into the lead store and writes draft replies.
DISABLED by default. To enable:
  1. pip install google-auth google-auth-oauthlib google-api-python-client
  2. Place an OAuth client JSON at credentials.json
  3. Run:  python -m caos.gmail authorize
  4. Then: caos pull          # pulls new threads as leads
          caos draft <id>     # writes a draft reply (does NOT send)

Auto-send is intentionally NOT supported. Joey reviews every reply.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path

from . import db, leads, messages

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
TOKEN_PATH = Path(os.environ.get("CAOS_GMAIL_TOKEN", "gmail_token.json"))
CREDS_PATH = Path(os.environ.get("CAOS_GMAIL_CREDS", "credentials.json"))
ENQUIRY_QUERY = os.environ.get("CAOS_GMAIL_QUERY", "newer_than:14d (enquiry OR booking OR event)")


def _load_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:
        raise RuntimeError(
            "Gmail integration requires: pip install "
            "google-auth google-auth-oauthlib google-api-python-client"
        ) from e

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDS_PATH.exists():
                raise RuntimeError(f"missing OAuth client at {CREDS_PATH}")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def authorize() -> str:
    _load_service()
    return f"authorized — token saved to {TOKEN_PATH}"


# --- Heuristic enquiry parser ----------------------------------------------

_DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
_GUESTS_RE = re.compile(r"\b(\d{2,4})\s*(guests?|people|pax|heads)\b", re.I)
_EVENT_TYPES = (
    "wedding", "birthday", "engagement", "corporate", "anniversary",
    "christening", "baby shower", "function", "private event",
)


def parse_enquiry(body: str) -> dict:
    """Extract structured fields from a free-form enquiry email body."""
    body_l = body.lower()
    out: dict = {}

    m = _DATE_RE.search(body)
    if m:
        out["event_date"] = m.group(1)

    m = _GUESTS_RE.search(body)
    if m:
        out["guest_count"] = int(m.group(1))

    for et in _EVENT_TYPES:
        if et in body_l:
            out["event_type"] = et
            break

    return out


# --- Sync ------------------------------------------------------------------

def pull(conn: sqlite3.Connection, max_results: int = 50) -> list[int]:
    """Pull recent enquiry threads and create leads. Returns new lead ids."""
    svc = _load_service()
    res = svc.users().messages().list(
        userId="me", q=ENQUIRY_QUERY, maxResults=max_results
    ).execute()
    new_ids: list[int] = []
    for ref in res.get("messages", []):
        msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
        thread_id = msg.get("threadId")
        # Skip if we already created a lead for this thread.
        existing = conn.execute(
            "SELECT id FROM leads WHERE source = ?", (f"gmail:{thread_id}",)
        ).fetchone()
        if existing:
            continue

        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        body = _extract_body(msg["payload"])
        parsed = parse_enquiry(body)
        lead_id = leads.create(
            conn,
            name=headers.get("from", "Unknown").split("<")[0].strip(),
            contact=headers.get("from", ""),
            event_type=parsed.get("event_type"),
            event_date=parsed.get("event_date"),
            guest_count=parsed.get("guest_count"),
            source=f"gmail:{thread_id}",
            status="NEW",
            notes=f"Subject: {headers.get('subject', '')}",
        )
        db.log_event(conn, lead_id, "GMAIL_PULL", thread_id)
        new_ids.append(lead_id)
    return new_ids


def _extract_body(payload: dict) -> str:
    import base64
    if payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", "ignore")
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    return ""


def draft_reply(conn: sqlite3.Connection, lead_id: int) -> str:
    """Create a Gmail draft (NOT sent) for the given lead."""
    import base64
    from email.message import EmailMessage

    lead = leads.get(conn, lead_id)
    if not lead:
        raise ValueError(f"lead {lead_id} not found")
    if not (lead.get("source") or "").startswith("gmail:"):
        raise ValueError(f"lead {lead_id} is not a gmail thread")
    thread_id = lead["source"].split(":", 1)[1]
    msg = messages.for_lead(lead)

    svc = _load_service()
    em = EmailMessage()
    em.set_content(msg.body)
    em["To"] = lead.get("contact") or ""
    em["Subject"] = msg.subject

    raw = base64.urlsafe_b64encode(em.as_bytes()).decode()
    draft = svc.users().drafts().create(
        userId="me", body={"message": {"raw": raw, "threadId": thread_id}}
    ).execute()
    db.log_event(conn, lead_id, "GMAIL_DRAFT", json.dumps({"draft_id": draft.get("id")}))
    return draft.get("id", "")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "authorize":
        print(authorize())
    else:
        print(__doc__)

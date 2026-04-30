"""Smoke test exercising the full CAOS loop end-to-end with stdlib only.

Run with:  python -m tests.test_smoke
"""
from __future__ import annotations

import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    tmp = tempfile.mkdtemp(prefix="caos-test-")
    os.environ["CAOS_DB"] = str(Path(tmp) / "caos.db")

    from caos import db, leads, messages, triggers, dashboard, classifier

    db.init()

    with db.session() as conn:
        # 1. New HOT lead (date + guests)
        hot_id = leads.create(
            conn,
            name="Wedding Anna",
            event_type="wedding",
            event_date=(datetime.utcnow() + timedelta(days=40)).strftime("%Y-%m-%d"),
            guest_count=120,
            source="instagram",
            status="NEW",
        )
        hot = leads.get(conn, hot_id)
        assert hot["classification"] == "HOT", hot
        assert hot["priority_score"] >= 60

        # 2. WARM lead (only date)
        warm_id = leads.create(
            conn, name="Maybe Mike",
            event_type="birthday",
            event_date=(datetime.utcnow() + timedelta(days=200)).strftime("%Y-%m-%d"),
            status="NEW",
        )
        assert leads.get(conn, warm_id)["classification"] == "WARM"

        # 3. COLD lead (no info)
        cold_id = leads.create(conn, name="Vague Vanessa", status="NEW")
        assert leads.get(conn, cold_id)["classification"] == "COLD"

        # 4. Trigger: visit booked
        triggers.on_visit_booked(conn, hot_id)
        hot = leads.get(conn, hot_id)
        assert hot["status"] == "VISIT BOOKED"

        # 5. Trigger: visit completed → priority MAX, close message generated
        result = triggers.on_visit_completed(conn, hot_id)
        hot = leads.get(conn, hot_id)
        assert hot["status"] == "VISITED"
        assert hot["priority_score"] == 100
        assert hot["visit_completed_at"]
        assert "Quote attached" in (result.suggested_message or "")

        # 6. AT RISK sweep — age the warm lead's contact date.
        old = (datetime.utcnow() - timedelta(days=4)).strftime("%Y-%m-%d")
        leads.update(conn, warm_id, last_contact_date=old, status="CONTACTED")
        flagged = triggers.sweep_at_risk(conn)
        assert any(r.lead_id == warm_id for r in flagged), flagged
        assert leads.get(conn, warm_id)["at_risk"] == 1

        # 7. Message generation respects operator rules
        warm_lead = leads.get(conn, warm_id)
        msg = messages.for_lead(warm_lead)
        violations = messages.lint(msg)
        assert violations == [], violations
        assert "checking in" not in msg.body.lower()
        assert any(token in msg.body for token in ("YES", "NO", "NOT NOW", "?"))

        # 8. Dashboard renders without error and includes lane headers.
        rendered = dashboard.render(conn)
        assert "CAOS" in rendered
        assert "CLOSE NOW" in rendered

        # 9. Re-classify everything (idempotent).
        n = leads.recompute_all(conn)
        assert n >= 3

    print("OK — CAOS smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

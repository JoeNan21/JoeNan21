"""CAOS command-line interface — the operator's interface to the closing engine.

Commands:
  init                              Initialise the local DB
  seed                              Load demo leads
  console                           Render the Daily Command Console
  add ...                           Add a new lead (triggers NEW_LEAD)
  show <id>                         Show a lead + its suggested message
  msgs <id>                         Show all message variants for a lead
  contact <id> [--note "..."]       Mark contact made (clears AT RISK)
  booked <id>                       Trigger: visit booked
  visited <id>                      Trigger: visit completed (priority MAX, 24h timer)
  status <id> <STATUS>              Set status manually
  proposal <id>                     Mark PROPOSAL sent
  close <id>                        Mark CLOSED
  lost <id>                         Mark LOST
  sweep                             Run the AT RISK sweep (cron-friendly)
  recompute                         Re-classify and re-score all leads
  pull                              [Gmail] Import enquiry threads
  draft <id>                        [Gmail] Create a Gmail draft (not sent)
"""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

from . import dashboard, db, leads, messages, triggers


def _add_lead_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--name", required=True)
    p.add_argument("--contact")
    p.add_argument("--event-type", dest="event_type")
    p.add_argument("--date", dest="event_date")
    p.add_argument("--guests", dest="guest_count", type=int)
    p.add_argument("--source")
    p.add_argument("--status", default="NEW")
    p.add_argument("--notes")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="caos",
        description="CAOS — closing engine for Sorrento in the Park",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="initialise the local DB")
    sub.add_parser("seed", help="load demo leads")
    sub.add_parser("console", help="render the Daily Command Console")

    add = sub.add_parser("add", help="add a new lead")
    _add_lead_args(add)

    show = sub.add_parser("show", help="show a single lead")
    show.add_argument("id", type=int)

    msgs = sub.add_parser("msgs", help="show all message variants")
    msgs.add_argument("id", type=int)

    contact = sub.add_parser("contact", help="mark contact made")
    contact.add_argument("id", type=int)
    contact.add_argument("--note")

    for name, help_text in (
        ("booked", "trigger visit booked"),
        ("visited", "trigger visit completed"),
        ("proposal", "mark PROPOSAL sent"),
        ("close", "mark CLOSED"),
        ("lost", "mark LOST"),
    ):
        sp = sub.add_parser(name, help=help_text)
        sp.add_argument("id", type=int)

    status = sub.add_parser("status", help="set status manually")
    status.add_argument("id", type=int)
    status.add_argument("status")

    sub.add_parser("sweep", help="run AT RISK sweep")
    sub.add_parser("recompute", help="re-classify and re-score every lead")

    sub.add_parser("pull", help="[Gmail] import enquiry threads")
    draft = sub.add_parser("draft", help="[Gmail] create a draft reply")
    draft.add_argument("id", type=int)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "init":
        db.init()
        print("CAOS initialised.")
        return 0

    if args.cmd == "seed":
        from . import seed as seed_module  # local import to avoid cycle
        db.init()
        with db.session() as conn:
            count = seed_module.load(conn)
        print(f"Seeded {count} leads.")
        return 0

    db.init()

    if args.cmd == "console":
        with db.session() as conn:
            triggers.sweep_at_risk(conn)
            print(dashboard.render(conn))
        return 0

    if args.cmd == "add":
        with db.session() as conn:
            lead_id = leads.create(
                conn,
                name=args.name,
                contact=args.contact,
                event_type=args.event_type,
                event_date=args.event_date,
                guest_count=args.guest_count,
                source=args.source,
                status=args.status,
                notes=args.notes,
            )
            result = triggers.on_new_lead(conn, lead_id)
        print(f"Lead #{lead_id} added · {result.action}")
        if result.suggested_message:
            print()
            print("--- SUGGESTED FIRST RESPONSE ---")
            print(result.suggested_message)
        return 0

    if args.cmd == "show":
        with db.session() as conn:
            lead = leads.get(conn, args.id)
        if not lead:
            print(f"lead {args.id} not found", file=sys.stderr)
            return 1
        print(dashboard.render_lead_detail(lead))
        return 0

    if args.cmd == "msgs":
        with db.session() as conn:
            lead = leads.get(conn, args.id)
        if not lead:
            print(f"lead {args.id} not found", file=sys.stderr)
            return 1
        print(dashboard.render_messages(lead))
        return 0

    if args.cmd == "contact":
        with db.session() as conn:
            lead = leads.mark_contacted(conn, args.id, note=args.note)
        print(f"Lead #{lead['id']} · contact logged · score={lead['priority_score']}")
        return 0

    if args.cmd == "booked":
        with db.session() as conn:
            r = triggers.on_visit_booked(conn, args.id)
        print(f"Lead #{r.lead_id} · {r.action}")
        return 0

    if args.cmd == "visited":
        with db.session() as conn:
            r = triggers.on_visit_completed(conn, args.id)
        print(f"Lead #{r.lead_id} · {r.action}")
        if r.suggested_message:
            print()
            print("--- SUGGESTED CLOSE MESSAGE ---")
            print(r.suggested_message)
        return 0

    if args.cmd == "status":
        with db.session() as conn:
            lead = leads.set_status(conn, args.id, args.status)
        print(f"Lead #{lead['id']} · status={lead['status']} · score={lead['priority_score']}")
        return 0

    if args.cmd in {"proposal", "close", "lost"}:
        target = {"proposal": "PROPOSAL", "close": "CLOSED", "lost": "LOST"}[args.cmd]
        with db.session() as conn:
            lead = leads.set_status(conn, args.id, target)
        print(f"Lead #{lead['id']} · {target}")
        return 0

    if args.cmd == "sweep":
        with db.session() as conn:
            results = triggers.sweep_at_risk(conn)
        if not results:
            print("Sweep clean — no leads flagged AT RISK.")
            return 0
        print(f"Flagged {len(results)} lead(s) AT RISK:")
        for r in results:
            print(f"  · #{r.lead_id} — {r.action}")
            if r.suggested_message:
                print("    " + r.suggested_message.splitlines()[0])
        return 0

    if args.cmd == "recompute":
        with db.session() as conn:
            n = leads.recompute_all(conn)
        print(f"Recomputed {n} leads.")
        return 0

    if args.cmd == "pull":
        from . import gmail
        with db.session() as conn:
            ids = gmail.pull(conn)
        print(f"Pulled {len(ids)} new lead(s): {ids}")
        return 0

    if args.cmd == "draft":
        from . import gmail
        with db.session() as conn:
            draft_id = gmail.draft_reply(conn, args.id)
        print(f"Draft created: {draft_id}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

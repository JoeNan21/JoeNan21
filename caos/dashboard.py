"""Daily Command Console.

This is the operator's morning view. Four lanes, sorted by priority:
   ⚡ CLOSE NOW   — post-visit leads inside the 24h window
   🔥 HOT         — lock the date, highest revenue
   ⏳ AT RISK     — flagged stale, last call
   🧊 LOW         — cold + warm without urgency

Renders with `rich` if available; falls back to plain ASCII.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from . import leads, messages, triggers

try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    HAS_RICH = True
except ImportError:  # graceful degradation
    HAS_RICH = False


LANE_CLOSE_NOW = "CLOSE NOW"
LANE_HOT = "HOT"
LANE_AT_RISK = "AT RISK"
LANE_LOW = "LOW"


def lanes(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    all_leads = leads.list_all(conn, include_dead=False)
    close_now_ids = {l["id"] for l in triggers.overdue_close_timers(conn)}

    out: dict[str, list[dict]] = {
        LANE_CLOSE_NOW: [],
        LANE_HOT: [],
        LANE_AT_RISK: [],
        LANE_LOW: [],
    }
    for lead in all_leads:
        status = (lead.get("status") or "").upper()
        if status in {"VISITED", "PROPOSAL"}:
            out[LANE_CLOSE_NOW].append(lead)
        elif lead.get("at_risk"):
            out[LANE_AT_RISK].append(lead)
        elif lead.get("classification") == "HOT":
            out[LANE_HOT].append(lead)
        else:
            out[LANE_LOW].append(lead)

    for lane in out.values():
        lane.sort(key=lambda l: (l.get("priority_score") or 0), reverse=True)

    # Mark close-now overdues so the renderer can highlight them.
    for lead in out[LANE_CLOSE_NOW]:
        lead["_overdue"] = lead["id"] in close_now_ids

    return out


LANE_META = {
    LANE_CLOSE_NOW: ("⚡ CLOSE NOW",  "post-visit — close in 24h",  "bold red"),
    LANE_HOT:       ("🔥 HOT LEADS",   "lock the date",               "bold yellow"),
    LANE_AT_RISK:   ("⏳ AT RISK",     "stale — last call",           "bold magenta"),
    LANE_LOW:       ("🧊 LOW",         "warm/cold backlog",           "cyan"),
}


def render(conn: sqlite3.Connection) -> str:
    data = lanes(conn)
    if HAS_RICH:
        return _render_rich(data)
    return _render_plain(data)


def _render_rich(data: dict[str, list[dict]]) -> str:
    console = Console(record=True, width=120)
    console.print()
    console.print(Panel.fit(
        "[bold white]CAOS — Closing Command Centre[/bold white]\n"
        "[dim]Sorrento in the Park · Capture → Qualify → Advance → Close → Repeat[/dim]",
        border_style="bright_white",
    ))

    for lane_key, leads_in_lane in data.items():
        title, subtitle, style = LANE_META[lane_key]
        table = Table(
            title=f"{title}  [dim]· {subtitle}[/dim]",
            title_justify="left",
            box=box.SIMPLE_HEAVY,
            border_style=style,
            header_style=style,
            expand=True,
        )
        table.add_column("#", justify="right", width=4)
        table.add_column("Score", justify="right", width=6)
        table.add_column("Class", width=6)
        table.add_column("Status", width=14)
        table.add_column("Lead", overflow="fold")
        table.add_column("Event", overflow="fold")
        table.add_column("Date", width=12)
        table.add_column("Guests", justify="right", width=7)
        table.add_column("Last", width=12)

        if not leads_in_lane:
            table.add_row("—", "—", "—", "—", "[dim]nothing here[/dim]", "—", "—", "—", "—")
        else:
            for lead in leads_in_lane:
                row_style = ""
                if lead.get("_overdue"):
                    row_style = "bold red"
                elif (lead.get("priority_score") or 0) >= 90:
                    row_style = "bold"
                table.add_row(
                    str(lead["id"]),
                    str(lead.get("priority_score") or 0),
                    lead.get("classification") or "—",
                    lead.get("status") or "—",
                    lead.get("name") or "—",
                    lead.get("event_type") or "—",
                    str(lead.get("event_date") or "—"),
                    str(lead.get("guest_count") or "—"),
                    str(lead.get("last_contact_date") or "—"),
                    style=row_style,
                )
        console.print(table)

    console.print()
    console.print(Panel.fit(
        "[bold]Next moves:[/bold]  caos act <id>   ·   caos contact <id>   ·   caos visited <id>   ·   caos close <id>",
        border_style="bright_white",
    ))
    return console.export_text()


def _render_plain(data: dict[str, list[dict]]) -> str:
    lines = ["", "=" * 80, "CAOS — Closing Command Centre", "=" * 80]
    for lane_key, leads_in_lane in data.items():
        title, subtitle, _ = LANE_META[lane_key]
        lines.append("")
        lines.append(f"{title}  ·  {subtitle}")
        lines.append("-" * 80)
        if not leads_in_lane:
            lines.append("  (empty)")
            continue
        lines.append(f"  {'ID':>4} {'SCORE':>6} {'CLS':<6} {'STATUS':<14} {'NAME':<22} {'EVENT':<14} {'DATE':<12} {'GST':>4}")
        for lead in leads_in_lane:
            lines.append(
                f"  {lead['id']:>4} "
                f"{(lead.get('priority_score') or 0):>6} "
                f"{(lead.get('classification') or '-'):<6} "
                f"{(lead.get('status') or '-'):<14} "
                f"{(lead.get('name') or '-')[:22]:<22} "
                f"{(lead.get('event_type') or '-')[:14]:<14} "
                f"{str(lead.get('event_date') or '-'):<12} "
                f"{str(lead.get('guest_count') or '-'):>4}"
            )
    lines.append("")
    lines.append("Next moves: caos act <id> · caos contact <id> · caos visited <id> · caos close <id>")
    lines.append("")
    return "\n".join(lines)


def render_lead_detail(lead: dict) -> str:
    """Detail view for a single lead with the suggested message."""
    msg = messages.for_lead(lead)
    if HAS_RICH:
        console = Console(record=True, width=100)
        console.print()
        console.print(Panel(
            f"[bold]{lead.get('name')}[/bold]  ·  "
            f"[yellow]{lead.get('classification') or '-'}[/yellow]  ·  "
            f"score [bold]{lead.get('priority_score') or 0}[/bold]  ·  "
            f"status [cyan]{lead.get('status')}[/cyan]"
            + ("  ·  [bold red]AT RISK[/bold red]" if lead.get("at_risk") else ""),
            title=f"Lead #{lead['id']}",
            border_style="bright_white",
        ))
        details = Table(box=box.SIMPLE, show_header=False, expand=True)
        details.add_row("Event",       str(lead.get("event_type") or "—"))
        details.add_row("Date",        str(lead.get("event_date") or "—"))
        details.add_row("Guests",      str(lead.get("guest_count") or "—"))
        details.add_row("Source",      str(lead.get("source") or "—"))
        details.add_row("Contact",     str(lead.get("contact") or "—"))
        details.add_row("Last contact",str(lead.get("last_contact_date") or "—"))
        details.add_row("Next action", str(lead.get("next_action_date") or "—"))
        if lead.get("notes"):
            details.add_row("Notes", lead["notes"])
        console.print(details)

        console.print(Panel(
            msg.body,
            title=f"Suggested message · {msg.kind}",
            subtitle=msg.subject,
            border_style="green",
        ))
        violations = messages.lint(msg)
        if violations:
            console.print(Panel(
                "\n".join(f"• {v}" for v in violations),
                title="Operator-rule violations",
                border_style="red",
            ))
        return console.export_text()

    parts = [
        "",
        f"Lead #{lead['id']}  {lead.get('name')}  [{lead.get('classification')} / {lead.get('priority_score')}]",
        f"Status: {lead.get('status')}" + ("  AT RISK" if lead.get("at_risk") else ""),
        f"Event:  {lead.get('event_type') or '-'}  on {lead.get('event_date') or '-'}  "
        f"({lead.get('guest_count') or '-'} guests)",
        f"Source: {lead.get('source') or '-'}",
        f"Contact: {lead.get('contact') or '-'}",
        f"Last contact: {lead.get('last_contact_date') or '-'}   Next: {lead.get('next_action_date') or '-'}",
        "",
        f"--- {msg.kind} ---",
        msg.render(),
    ]
    return "\n".join(parts)


def render_messages(lead: dict) -> str:
    bundle = messages.all_for_lead(lead)
    if HAS_RICH:
        console = Console(record=True, width=100)
        for kind, msg in bundle.items():
            console.print(Panel(
                msg.body,
                title=kind.upper().replace("_", " "),
                subtitle=msg.subject,
                border_style="green",
            ))
        return console.export_text()
    return "\n\n".join(
        f"=== {kind.upper()} ===\n{msg.render()}" for kind, msg in bundle.items()
    )


def stale_summary(lanes_data: Iterable[dict]) -> list[dict]:
    return [l for l in lanes_data if l.get("at_risk")]

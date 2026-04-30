# CAOS — Community Asset Operating System

**Live revenue execution system for Sorrento in the Park.**

This is not a CRM. This is a closing engine.

```
Capture → Qualify → Advance → Close → Repeat
```

CAOS tells Joey **who to contact, what to say, and when to close.**

---

## Quick start

```bash
# 1. (optional) install rich for the colour dashboard
pip install -r requirements.txt

# 2. initialise + load demo leads
python caos.py init
python caos.py seed

# 3. run the Daily Command Console
python caos.py console
```

The console renders four lanes, sorted by priority score:

| Lane            | What it shows                                     |
|-----------------|---------------------------------------------------|
| ⚡ **CLOSE NOW** | Post-visit leads — close in the 24h window       |
| 🔥 **HOT**       | Date + guest count locked, not yet visited        |
| ⏳ **AT RISK**   | No contact in 24-48h+ — last-call message ready   |
| 🧊 **LOW**       | Warm/cold backlog — qualify or release            |

---

## The closing loop

Every command moves a deal forward.

```bash
caos add --name "Maria" --event-type wedding --date 2026-06-14 --guests 140 --source instagram
#   → classifies HOT, generates first-response message

caos contact 1 --note "called, leaving voicemail"
#   → logs contact, clears AT RISK

caos booked 1
#   → status=VISIT BOOKED, priority bumped

caos visited 1
#   → status=VISITED, priority=100, 24h close timer started, close message generated

caos proposal 1     # quote sent
caos close 1        # deposit received → CLOSED
caos lost 1         # gone cold → LOST (drops out of console)
```

Inspect or message any lead at any time:

```bash
caos show 1         # detail view + the right message for the lead's state
caos msgs 1         # all four message variants (first / follow-up / close / at-risk)
```

---

## Automation triggers

| Trigger              | Fires when                       | Effect                                     |
|----------------------|----------------------------------|--------------------------------------------|
| `NEW_LEAD`           | `caos add`                       | Classify HOT/WARM/COLD + suggest response  |
| `VISIT_BOOKED`       | `caos booked <id>`               | Bump priority                              |
| `VISIT_COMPLETED`    | `caos visited <id>`              | Priority = 100, start 24h timer, close msg |
| `AT_RISK`            | `caos sweep` (24-48h since contact) | Flag + emit last-call message            |

Run `caos sweep` from cron or manually before each console:

```bash
caos sweep    # idempotent — re-flags any newly stale leads
```

The console runs the sweep automatically on every render.

---

## Operator rules (built into every message)

1. **No passive language.** "Just checking in" is banned and linted out.
2. **Always push YES / NO / NOT NOW.** Every message demands a decision.
3. **Short.** 1–4 lines, max.
4. **Move the deal forward.** Site visit OR decision — nothing else.

The lint check runs on every generated message. Violations show up in the
detail view (`caos show <id>`) so Joey sees them before sending.

---

## Classification + priority scoring

```
HOT  = post-visit  OR  (firm date AND guest count)
WARM = partial info (date OR guest count, not both)
COLD = low info
```

Priority score (0–100) blends:

- Base from classification (HOT 60 / WARM 35 / COLD 15)
- **Post-visit → 100, always** (24h close window)
- `VISIT BOOKED` → +15
- Guest count → up to +10 (revenue weighting)
- Date proximity → +10 if within 30 days, +5 within 90
- AT RISK flag → +10
- Stale decay → −1/day past 7 days since contact (capped −10)

---

## Optional: Gmail integration

Off by default. To enable enquiry pull + draft replies (auto-send is **never**
supported — every reply is reviewed by Joey):

```bash
pip install google-auth google-auth-oauthlib google-api-python-client

# Place an OAuth client at credentials.json, then:
python -m caos.gmail authorize

caos pull         # imports recent enquiry threads as leads
caos draft 12     # creates a Gmail draft reply for lead 12
```

Tune the search query with `CAOS_GMAIL_QUERY` (defaults to enquiries from the
last 14 days).

---

## Data model

Local SQLite at `./caos.db` (override with `CAOS_DB=/path/to/db`).

`leads` table columns:
`name, contact, event_type, event_date, guest_count, source, status,
classification, priority_score, last_contact_date, next_action_date,
visit_completed_at, at_risk, notes, created_at, updated_at`

Status values: `NEW · CONTACTED · VISIT BOOKED · VISITED · PROPOSAL · CLOSED · LOST`

Every state change is journalled into `lead_events` for audit.

---

## Tests

```bash
python -m tests.test_smoke
```

Walks the full loop: create HOT/WARM/COLD leads → trigger visit booked →
trigger visit completed → run at-risk sweep → render dashboard.

---

## Why this exists

Joey was tracking deals manually. CAOS removes him from that loop:

- Every morning: open the console.
- Top of the list = who to contact next.
- Every lead has the message already drafted.
- Stale deals get auto-flagged and a last-call message generated.

Speed and conversion. Nothing else.

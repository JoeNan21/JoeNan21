# CLAUDE.md — CAOS Revenue OS

> This is the single source of truth for building and running CAOS.
> Read this in full at the start of every session before touching any file.
> Treat this as both the build instruction and persistent project brain.

---

## WHAT THIS IS

**CAOS** — Community Asset Operating System

A revenue execution web app for **Sorrento in the Park**, a premium event venue in Cornwall Park, Auckland, New Zealand.

This is NOT a CRM.

Every screen must:

- Force a decision
- Create a next action
- Move a deal forward

No passive UI. No clutter. No dashboards for the sake of dashboards.

**Core loop:** Capture → Qualify → Advance → Close → Repeat

---

## OPERATOR

**Joey Nanai** (Misa Joey Nanai — chiefly title: Misa)

- Role: Co-owner and Brand Manager, Sorrento in the Park
- Background: Samoan Kiwi. 20+ years in B2B, IT services, consulting. Founder of Nanai Consulting.
- Philosophy: *O le ala i le pule o le tautua* — leadership through service
- Sales method: NEPQ + Sandler + JMM + Voss hybrid
  - Disqualify fast
  - Push for decisions
  - High-status, low-neediness
  - Frame control throughout
- Usage: Mobile-first. Often one-handed. Needs action in under 30 seconds.

---

## VENUE

**Sorrento in the Park** — Cornwall Park, Tāmaki Makaurau Auckland

Rooms:

- Pohutukawa — up to 80 guests
- Manukau — up to 220 guests
- Somerset — up to 60 guests

Event types:

- Weddings
- Corporate events & conferences
- Funeral receptions & unveilings
- Cultural events
- Private celebrations

Deal range: $3,000–$25,000+

Key team:

- Shirley — venue manager (email only)
- Vicky — co-owner, qualified accountant
- Kerry — building JotForm system
- Dan — Google Business Profile

**Core conversion rule:**
The site visit is the highest-conversion event.
Everything drives toward a visit or a confirmed booking.

---

## TECH STACK

```
React + Vite + TypeScript
Tailwind CSS + shadcn/ui
React Router (client-side routing)
Recharts (forecast charts)
localStorage — all persistence, no backend
Anthropic Claude API — claude-sonnet-4-20250514
```

API key stored in localStorage under key: `caos_api_key`
Never hardcoded. Never logged.

---

## PROJECT STRUCTURE

```
/src
  /components
    /ui              # shadcn/ui primitives
    /leads           # LeadCard, LeadDetail, LeadForm, KanbanBoard
    /brief           # MorningBrief, PriorityBanner, OverdueList
    /pipeline        # KanbanView, ListView, FilterBar
    /composer        # MessageComposer, MessageTypeSelector
    /forecast        # ForecastChart, PipelineReview, HealthScore
    /tools           # CallPrep, CallSummary
    /settings        # SettingsPanel
    /layout          # AppShell, BottomNav, Sidebar, NavItem
  /hooks
    useLeads.ts      # All lead CRUD + localStorage sync
    useSettings.ts   # API key, targets, room blocks
    useClaude.ts     # Anthropic API call wrapper
    usePriority.ts   # Priority scoring + sorting logic
  /lib
    priority.ts      # Priority logic (pure functions)
    claude.ts        # API call builder + system prompt
    storage.ts       # localStorage read/write helpers
    dates.ts         # Date gap calculations, colour logic
    sampleData.ts    # Pre-populated leads for first load
  /types
    index.ts         # All TypeScript types
  /pages
    Brief.tsx
    Pipeline.tsx
    Composer.tsx
    Forecast.tsx
    Tools.tsx
    Settings.tsx
  App.tsx
  main.tsx
```

---

## DATA MODEL

```typescript
type EventType = 'wedding' | 'corporate' | 'funeral' | 'cultural' | 'private'
type Stage = 'new' | 'contacted' | 'visit-booked' | 'post-visit' | 'confirmed' | 'lost'
type Room = 'pohutukawa' | 'manukau' | 'somerset' | null
type ContactMethod = 'email' | 'phone' | 'social' | 'referral' | 'walk-in'

interface Lead {
  id: string
  name: string
  eventType: EventType
  eventDate: string | null           // ISO date string
  guestCount: number | null
  contactMethod: ContactMethod
  stage: Stage
  estimatedValue: number | null
  enquiryDate: string                // ISO date string
  lastContact: string                // ISO date string
  visitDate: string | null           // ISO date string
  followUpDue: string | null         // ISO date string
  depositReceived: boolean
  depositAmount: number | null       // actual deposit taken (may differ from estimatedValue)
  room: Room
  notes: string                      // Append-only interaction log with timestamps
  competingVenues: string[]
  source: string
}

interface Settings {
  operatorName: string               // default: 'Joey'
  venueName: string                  // default: 'Sorrento in the Park'
  apiKey: string
  monthlyTargets: Record<string, number>   // key: 'YYYY-MM', value: target in NZD
  roomBlocks: RoomBlock[]
}

interface RoomBlock {
  id: string
  room: Room
  date: string                       // ISO date
  reason: string
}
```

---

## STAGE DEFINITIONS

| Stage | Description |
|---|---|
| `new` | Enquiry received, no reply sent |
| `contacted` | Initial reply sent, visit not booked |
| `visit-booked` | Site visit scheduled |
| `post-visit` | Visit completed, awaiting deposit |
| `confirmed` | Deposit received, date locked |
| `lost` | Not proceeding |

---

## PRIORITY ENGINE

Used for sorting, morning brief, follow-up flags. Apply everywhere.

```typescript
function getPriorityScore(lead: Lead): number {
  const now = Date.now()
  const hoursSinceEnquiry = (now - new Date(lead.enquiryDate).getTime()) / 3600000
  const hoursSinceVisit = lead.visitDate
    ? (now - new Date(lead.visitDate).getTime()) / 3600000 : null
  const hoursSinceContact = (now - new Date(lead.lastContact).getTime()) / 3600000

  if (lead.stage === 'new' && hoursSinceEnquiry > 24) return 100
  if (lead.stage === 'post-visit' && hoursSinceVisit && hoursSinceVisit > 48) return 95
  if (lead.stage === 'visit-booked' && isToday(lead.visitDate)) return 90
  if (lead.stage === 'contacted' && hoursSinceContact > 120) return 80
  if (lead.stage === 'post-visit' && hoursSinceVisit && hoursSinceVisit <= 48) return 75
  if ((lead.estimatedValue ?? 0) > 10000 && hoursSinceContact > 72) return 70
  return 10
}
```

---

## FORECAST RULES

Stage probability weightings:

| Stage | Weight |
|---|---|
| new | 10% |
| contacted | 20% |
| visit-booked | 40% |
| post-visit | 65% |
| confirmed | 100% |
| lost | 0% |

Confirmed revenue calculation:

- Use `depositAmount` if present
- Fallback to `estimatedValue` if `depositAmount` is null

---

## CLAUDE API SYSTEM PROMPT

Use this verbatim as the system prompt for ALL Claude API calls.
Do not modify without updating this file.

```
You are a revenue execution agent for Sorrento in the Park, a premium event venue in Cornwall Park, Auckland, New Zealand.

You support Joey Nanai — a high-performance venue sales closer. Your job: move leads toward site visits and bookings, faster.

COMMUNICATION FRAMEWORK (JMM):
- Signal over noise — no filler, no generic phrases, never say "just checking in"
- Non-needy frame — never chase, never over-explain, always offer value and direction
- Directional control — every message ends with a clear next step, decision point, or direct question
- Short messages: 1–3 short paragraphs, easy to reply to on a phone
- Plain text only in all message drafts — no markdown, no bullet points, no bold
- Pattern interrupts used lightly: "Quick one", "Worth a look", "Out of curiosity"
- Status positioning: Sorrento is in-demand, considered, worth seeing in person

TONE BY EVENT TYPE:
- Weddings: warm, confident, vision-focused, celebratory
- Corporate: clear, efficient, low-friction, logistics-aware
- Cultural: energetic, group-aware, atmospheric
- Funerals/unveilings: empathetic first, calm, simple — remove all friction, zero pressure, no hard close

TONE BY TIME GAP:
- Under 24h: light and natural
- 1–3 days: directional, momentum-building
- 3–7 days: firmer, create urgency
- 7+ days: re-engagement reset
- 30+ days: reactivation — treat as near-new

VENUE:
- Sorrento in the Park, Cornwall Park, Auckland
- Rooms: Pohutukawa (80 cap), Manukau (220 cap), Somerset (60 cap)
- Deal range: $3,000–$25,000+
- Site visit = highest-conversion event. Everything moves toward a visit or a confirmed booking.

OPERATOR PHILOSOPHY:
- Joey closes. You support, not replace.
- Momentum beats perfection.
- Every lead must move forward, close out, or be clearly parked.
- No passive behaviour. No open-ended drift.
```

---

## useClaude HOOK — BEHAVIOUR RULES

- Model: `claude-sonnet-4-20250514` always
- Max tokens: 1000
- API key from `settings.apiKey` (localStorage under `caos_api_key`)
- If API key missing: surface a clear inline prompt to set it in Settings — not an error throw, not an alert
- All calls are async with `isGenerating: boolean` loading state
- Never call the API on mount — only on explicit user action (button press)
- Errors surface inline in the component

---

## DESIGN SYSTEM

Dark theme only.

```css
--bg-base: #0a0a0a;
--bg-surface: #111111;
--bg-elevated: #1a1a1a;
--bg-border: #2a2a2a;
--accent-gold: #c9a84c;
--accent-teal: #2a6b6b;
--text-primary: #f0ede8;
--text-muted: #9a9590;
--status-green: #22c55e;
--status-amber: #f59e0b;
--status-red: #ef4444;
--radius: 8px;
--font: 'Inter', sans-serif;
```

Days-since-contact colour logic (apply everywhere):

- ≤24h → `--status-green`
- 24–48h → `--status-amber`
- 48h+ → `--status-red`

---

## UX RULES — NON-NEGOTIABLE

1. Stage changes are instant — no save button, write to localStorage immediately
2. Every AI output is copyable with one tap (copy icon, minimum 44px target)
3. Days-since-contact colour coding on every lead card and row
4. No modals for reading — use slide-in drawers and panels
5. Single confirmation only for destructive actions: 'lost', delete
6. AI calls always show pulsing "Generating…" state — never blank, never frozen
7. Mobile-first — build and test at 375px first, 768px+ second
8. No hover-only interactions anywhere
9. Touch targets minimum 44px height
10. Kanban: horizontal scroll with snap on mobile — do not stack columns vertically
11. Kanban drag-and-drop must work with touch (use touch-compatible DnD library)
12. API key masked after entry — show last 4 chars only (e.g. `••••••••a1b2`)
13. localStorage write on every lead mutation — no data loss on refresh
14. Empty states drive action — never just "No data found"

---

## NAVIGATION

Mobile — bottom nav (sticky, z-50):

| Tab | Label | Route |
|---|---|---|
| 📋 | Brief | `/` |
| 📊 | Pipeline | `/pipeline` |
| ✉️ | Draft | `/composer` |
| 📈 | Forecast | `/forecast` |
| 🛠 | Tools | `/tools` |

Desktop — left sidebar (240px, fixed):
Same 5 items + Settings gear icon at bottom

Active state: `--accent-gold` on icon and label

Settings reachable in 1 tap from any screen at all times.

---

## SUCCESS CRITERIA

Open the app.

Within 10 seconds → know what matters.
Within 30 seconds → send the right message.

Result → more bookings closed.

This is a revenue weapon, not software.

---

## BUILD ORDER

1. Types (`/src/types/index.ts`)
2. localStorage helpers (`/src/lib/storage.ts`)
3. `useLeads` hook + sample data
4. `useSettings` hook
5. `useClaude` hook
6. `usePriority` hook + priority logic
7. Navigation shell (bottom nav + sidebar)
8. Module 2 — Pipeline (Kanban + List + Lead Detail)
9. Module 1 — Morning Brief (static logic first, then AI)
10. Module 3 — Message Composer
11. Module 5 — Site Visit Tools (Call Prep + Call Summary)
12. Module 4 — Forecast + Pipeline Review
13. Module 6 — Settings

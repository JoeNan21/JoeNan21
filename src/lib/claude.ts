import type { Lead, MessageType } from '@/types'
import { EVENT_LABEL, ROOM_LABEL, STAGE_LABEL } from '@/types'
import { hoursSince, formatNZDate } from '@/lib/dates'

// Spec pinned claude-sonnet-4-20250514; that model ID has been retired.
// Using the current latest Sonnet. Update CLAUDE.md if this changes.
export const CLAUDE_MODEL = 'claude-sonnet-4-6'
export const MAX_TOKENS = 1000

export const SYSTEM_PROMPT = `You are a revenue execution agent for Sorrento in the Park, a premium event venue in Cornwall Park, Auckland, New Zealand.

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
- No passive behaviour. No open-ended drift.`

export interface ClaudeCallOptions {
  apiKey: string
  userPrompt: string
  maxTokens?: number
}

export async function callClaude({
  apiKey,
  userPrompt,
  maxTokens = MAX_TOKENS,
}: ClaudeCallOptions): Promise<string> {
  if (!apiKey) throw new Error('API_KEY_MISSING')

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
    },
    body: JSON.stringify({
      model: CLAUDE_MODEL,
      max_tokens: maxTokens,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: userPrompt }],
    }),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`Claude API error (${res.status}): ${text.slice(0, 300)}`)
  }

  const data = await res.json()
  const block = data?.content?.[0]
  if (!block || block.type !== 'text') {
    throw new Error('Unexpected Claude response shape')
  }
  return String(block.text).trim()
}

export function leadContextBlock(lead: Lead): string {
  const gap = hoursSince(lead.lastContact)
  const gapLine =
    gap == null
      ? 'No prior contact'
      : gap < 24
        ? `${Math.round(gap)}h since last contact`
        : `${Math.round(gap / 24)}d since last contact`

  return [
    `Name: ${lead.name}`,
    `Event: ${EVENT_LABEL[lead.eventType]}`,
    `Event date: ${formatNZDate(lead.eventDate)}`,
    `Guest count: ${lead.guestCount ?? 'unknown'}`,
    `Stage: ${STAGE_LABEL[lead.stage]}`,
    `Estimated value: ${lead.estimatedValue ? `$${lead.estimatedValue.toLocaleString()}` : 'unknown'}`,
    `Room: ${lead.room ? ROOM_LABEL[lead.room] : 'not assigned'}`,
    `Time gap: ${gapLine}`,
    lead.competingVenues.length ? `Competing: ${lead.competingVenues.join(', ')}` : 'Competing: none noted',
    lead.notes ? `Notes: ${lead.notes}` : 'Notes: none',
  ].join('\n')
}

const MESSAGE_TYPE_INSTRUCTIONS: Record<MessageType, string> = {
  'first-wedding':
    'Warm first reply to a wedding enquiry. Celebrate briefly. Ask at most two qualifying questions (guest count, rough date). End by offering a site visit with two specific times.',
  'first-corporate':
    'Clear, efficient first reply to a corporate enquiry. Acknowledge the event type. Ask at most two qualifiers (date/guest count/AV needs). Offer a site visit with two specific times.',
  'first-funeral':
    'Empathetic, simple first reply to a funeral or unveiling enquiry. Lead with care. No pricing push, no hard close. Offer to talk or host a visit at their convenience. Remove friction.',
  'first-private':
    'Warm first reply to a private celebration or cultural event. Light, welcoming, confident. Qualify guest count and rough date. Invite them to visit.',
  'first-vague':
    'First reply when event type or details are unclear. Friendly but directional. Ask one or two clarifying questions (event type, rough date). Invite them to share a bit more or book a visit.',
  'visit-invite':
    'They know the venue. Offer two specific site visit times. Confirm event context in one sentence. Keep it short, end on the CTA.',
  'post-visit-24h':
    'Day-after follow-up. Reference something specific from the visit notes. Warm but directional. End with a direct next step (deposit, hold, decision timeline).',
  'post-visit-48h':
    'Firmer post-visit follow-up. Gentle urgency. Reference a visit detail. Offer to hold the date for 48 hours or take a deposit.',
  'reengage-3-7':
    'Reopen a lead gone quiet for 3-7 days. Directional, create momentum. End with a clear decision question or a specific visit time.',
  'reengage-7plus':
    'Reset tone for a lead 7+ days quiet. Treat as near-new. No guilt, no chase. One clear question, one clear offer.',
  'final-close':
    'Decision push. Respectful but firm. Frame it as deposit now or step away. Two sentences max before the ask.',
  'deposit-request':
    'Direct ask to lock the date with deposit. Confirm the amount context and the next concrete step (send invoice, reply yes).',
  'date-hold':
    'Offer a 48-hour date hold while they decide. Confirm the date and room if known. End with the hold offer.',
  'stale-30d':
    'Reactivate an old enquiry (30+ days). Reset tone entirely. Low pressure. Ask if the event is still happening and offer a fresh visit.',
}

export function buildMessagePrompt(
  lead: Lead,
  messageType: MessageType,
  extraContext: string,
): string {
  return [
    MESSAGE_TYPE_INSTRUCTIONS[messageType],
    '',
    'LEAD CONTEXT:',
    leadContextBlock(lead),
    extraContext ? `\nEXTRA CONTEXT FROM OPERATOR:\n${extraContext}` : '',
    '',
    'RULES:',
    `- Use first name only — "Hi ${lead.name.split(/\s|&/)[0].trim()}". Never "Hi there".`,
    '- Reference their specific event type — never list all types.',
    '- Ask maximum two things when qualifying.',
    '- Offer two specific times when inviting to a visit.',
    '- End on the CTA. No filler after it.',
    '- Never say "I hope this email finds you well", "Looking forward to hearing from you", "Feel free to reach out".',
    '- Plain text only. No markdown, no bullet points, no bold.',
    '- Under 150 words.',
    '- No preamble. No explanation. Output the message body only, ready to send.',
  ]
    .filter(Boolean)
    .join('\n')
}

export function buildMorningPriorityPrompt(leads: Lead[]): string {
  const postVisit = leads.filter((l) => l.stage === 'post-visit')
  const summary = leads
    .filter((l) => l.stage !== 'lost' && l.stage !== 'confirmed')
    .map(
      (l) =>
        `- ${l.name} | ${l.eventType} | stage: ${l.stage} | last contact: ${formatNZDate(l.lastContact)} | value: $${l.estimatedValue ?? 0}`,
    )
    .join('\n')

  return [
    postVisit.length > 0
      ? `CLOSE DIRECTIVE: ${postVisit.length} lead${postVisit.length > 1 ? 's are' : ' is'} post-visit. These must close or park today — no drift.`
      : '',
    'You have the active pipeline below. Return ONE sentence stating the single most important action right now and why.',
    'No preamble. No list. No markdown. Just one direct sentence (max 30 words).',
    '',
    'PIPELINE:',
    summary || '(no active leads)',
  ]
    .filter(Boolean)
    .join('\n')
}

export function buildSuggestedActionsPrompt(leads: Lead[]): string {
  const summary = leads
    .filter((l) => l.stage !== 'lost' && l.stage !== 'confirmed')
    .map(
      (l) =>
        `- ${l.id} | ${l.name} | ${l.eventType} | stage: ${l.stage} | last contact: ${formatNZDate(l.lastContact)} | value: $${l.estimatedValue ?? 0}`,
    )
    .join('\n')

  return [
    'From the pipeline below, return EXACTLY three priority actions for today, in order of importance.',
    'Each action on its own line, plain text, no markdown, no numbering, no preamble.',
    'Format each line as: [lead name] — [specific action].',
    '',
    'PIPELINE:',
    summary || '(no active leads)',
  ].join('\n')
}

export function buildCallPrepPrompt(lead: Lead, prepType: string): string {
  return [
    `Generate a site visit prep brief for a ${prepType}.`,
    '',
    'LEAD CONTEXT:',
    leadContextBlock(lead),
    '',
    'Return the brief with these sections in order (plain text, short sentences, no markdown):',
    '1. WHO YOU\'RE MEETING — what\'s known, likely priorities, one tailored talking point',
    '2. THEIR EVENT SUMMARY — type, date, guest count, vision signals from notes',
    '3. RECOMMENDED ROOM — with rationale based on guest count (Pohutukawa 80 / Manukau 220 / Somerset 60)',
    '4. QUESTIONS TO ASK — 4-5 tailored questions designed to surface objections and decision timeline',
    '5. ANTICIPATED OBJECTIONS + RESPONSES — pricing, comparing venues, date availability, package flexibility',
    '6. CLOSING PLAN — goal (deposit or 48h hold), tailored closing line, fallback hold offer',
    '7. SUGGESTED VISIT AGENDA — 30-45 minute format',
    '8. ONE-LINE SUMMARY — who they are, what they need, goal today',
  ].join('\n')
}

export function buildCallSummaryPrompt(lead: Lead, rawNotes: string): string {
  return [
    'Process these raw visit notes into two outputs.',
    '',
    'LEAD CONTEXT:',
    leadContextBlock(lead),
    '',
    'RAW NOTES:',
    rawNotes,
    '',
    'OUTPUT FORMAT (plain text, no markdown):',
    '',
    '=== INTERNAL SUMMARY ===',
    'Event details: (type, date, guests, recommended room)',
    'Their vision / key requirements:',
    'Budget signals:',
    'Objections raised + status (addressed / open / needs follow-up):',
    'Competing venues mentioned:',
    'Decision timeline:',
    'Deal status: (Hot / Warm / Cold / Lost)',
    'Next step: (one most important action + deadline)',
    '',
    '=== FOLLOW-UP EMAIL ===',
    'A JMM-style follow-up email under 150 words that:',
    '- Opens with a specific reference from the visit notes (not generic)',
    '- Says in 1-2 sentences what resonated',
    '- Addresses any open concern',
    '- Closes with a direct deposit ask or 48-hour hold offer',
    '- Plain text only, no markdown, no bullet points',
  ].join('\n')
}

export function buildPipelineReviewPrompt(leads: Lead[]): string {
  const summary = leads
    .map(
      (l) =>
        `- ${l.name} | ${l.eventType} | stage: ${l.stage} | enquired: ${formatNZDate(l.enquiryDate)} | last contact: ${formatNZDate(l.lastContact)} | visit: ${formatNZDate(l.visitDate)} | value: $${l.estimatedValue ?? 0} | competing: ${l.competingVenues.join(', ') || 'none'}`,
    )
    .join('\n')

  return [
    'Review this pipeline and produce a weekly operator briefing.',
    '',
    'PIPELINE:',
    summary || '(empty)',
    '',
    'OUTPUT FORMAT (plain text, no markdown):',
    '',
    '=== PIPELINE HEALTH ===',
    'Overall score out of 100.',
    'Response speed (out of 25): score + one-line reason',
    'Follow-up recency (out of 25): score + one-line reason',
    'Stage progression (out of 25): score + one-line reason',
    'Pipeline coverage (out of 25): score + one-line reason',
    '',
    '=== RISK FLAGS ===',
    'List any: gone cold, high-value unworked, competing venues active.',
    '',
    '=== THIS WEEK ===',
    'Three specific actions in order of priority.',
  ].join('\n')
}

export function buildForecastSummaryPrompt(
  leads: Lead[],
  nextTarget: { month: string; target: number; confirmed: number; weighted: number },
): string {
  const summary = leads
    .filter((l) => l.stage !== 'lost')
    .map(
      (l) =>
        `- ${l.name} | ${l.eventType} | stage: ${l.stage} | event: ${formatNZDate(l.eventDate)} | value: $${l.estimatedValue ?? 0}`,
    )
    .join('\n')

  return [
    `Give a 2-3 sentence revenue outlook for ${nextTarget.month}.`,
    `Target: $${nextTarget.target}. Confirmed: $${nextTarget.confirmed}. Weighted pipeline: $${nextTarget.weighted}.`,
    'Say whether we are on track, behind, or ahead. Name the single biggest gap to focus on. Plain text only.',
    '',
    'PIPELINE:',
    summary || '(empty)',
  ].join('\n')
}

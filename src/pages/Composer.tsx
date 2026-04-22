import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { RefreshCw, Sparkles } from 'lucide-react'
import { useLeadsStore, useSettingsStore } from '@/store/LeadsContext'
import { useClaude } from '@/hooks/useClaude'
import { buildMessagePrompt } from '@/lib/claude'
import { Button } from '@/components/ui/Button'
import { CopyButton } from '@/components/ui/CopyButton'
import type { Lead, MessageType } from '@/types'
import { EVENT_LABEL } from '@/types'

const MESSAGE_TYPES: { value: MessageType; label: string; hint: string }[] = [
  { value: 'first-wedding', label: 'First Reply · Wedding', hint: 'Warm, celebratory' },
  { value: 'first-corporate', label: 'First Reply · Corporate', hint: 'Clear, efficient' },
  { value: 'first-funeral', label: 'First Reply · Funeral', hint: 'Empathetic, simple' },
  { value: 'first-private', label: 'First Reply · Private/Cultural', hint: 'Warm, welcoming' },
  { value: 'first-vague', label: 'First Reply · Vague', hint: 'Clarify gently' },
  { value: 'visit-invite', label: 'Site Visit Invitation', hint: 'Offer two specific times' },
  { value: 'post-visit-24h', label: 'Post-Visit · 24h', hint: 'Reference visit detail' },
  { value: 'post-visit-48h', label: 'Post-Visit · 48h+', hint: 'Firmer urgency' },
  { value: 'reengage-3-7', label: 'Re-engage · 3-7 days', hint: 'Reopen with direction' },
  { value: 'reengage-7plus', label: 'Re-engage · 7+ days', hint: 'Reset tone' },
  { value: 'final-close', label: 'Final Close', hint: 'Decision push' },
  { value: 'deposit-request', label: 'Deposit Request', hint: 'Direct ask' },
  { value: 'date-hold', label: 'Date Hold Offer', hint: '48-hour hold' },
  { value: 'stale-30d', label: 'Stale Reactivation · 30d+', hint: 'Low pressure reset' },
]

function defaultTypeForLead(lead: Lead | null): MessageType {
  if (!lead) return 'first-wedding'
  switch (lead.stage) {
    case 'new':
      return lead.eventType === 'wedding'
        ? 'first-wedding'
        : lead.eventType === 'corporate'
          ? 'first-corporate'
          : lead.eventType === 'funeral'
            ? 'first-funeral'
            : 'first-private'
    case 'contacted':
      return 'visit-invite'
    case 'visit-booked':
      return 'visit-invite'
    case 'post-visit':
      return 'post-visit-24h'
    case 'confirmed':
      return 'deposit-request'
    default:
      return 'first-vague'
  }
}

export function ComposerPage() {
  const { leads } = useLeadsStore()
  const { settings } = useSettingsStore()
  const [params, setParams] = useSearchParams()
  const initialLeadId = params.get('leadId')
  const [leadId, setLeadId] = useState<string>(initialLeadId ?? leads[0]?.id ?? '')
  const lead = useMemo(() => leads.find((l) => l.id === leadId) ?? null, [leads, leadId])
  const [messageType, setMessageType] = useState<MessageType>(defaultTypeForLead(lead))
  const [context, setContext] = useState('')
  const { output, error, isGenerating, generate } = useClaude(settings.apiKey)

  useEffect(() => {
    setMessageType(defaultTypeForLead(lead))
  }, [lead?.id, lead?.stage])

  const run = () => {
    if (!lead) return
    const prompt = buildMessagePrompt(lead, messageType, context)
    generate(prompt, 600)
  }

  const onSelectLead = (id: string) => {
    setLeadId(id)
    setParams((p) => {
      p.set('leadId', id)
      return p
    })
  }

  return (
    <div className="p-4 md:p-6 space-y-4 max-w-3xl mx-auto">
      <div>
        <h1 className="text-xl md:text-2xl font-semibold text-ink">Message Composer</h1>
        <div className="text-muted text-xs mt-0.5">
          JMM-style drafts. Plain text. Under 150 words. One tap to copy.
        </div>
      </div>

      <div className="card p-4 space-y-3">
        <div>
          <label className="label">Lead</label>
          <select
            className="input"
            value={leadId}
            onChange={(e) => onSelectLead(e.target.value)}
          >
            <option value="">— Select lead —</option>
            {leads.map((l) => (
              <option key={l.id} value={l.id}>
                {l.name} — {EVENT_LABEL[l.eventType]}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">Message Type</label>
          <select
            className="input"
            value={messageType}
            onChange={(e) => setMessageType(e.target.value as MessageType)}
          >
            {MESSAGE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label} — {t.hint}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">Extra Context (optional)</label>
          <textarea
            className="textarea"
            rows={3}
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g. Mention the pohutukawa trees. They're comparing with Wintergarden."
          />
        </div>

        <Button onClick={run} disabled={!lead || isGenerating} full>
          {isGenerating ? (
            <>
              <RefreshCw size={16} className="animate-spin" />
              Generating…
            </>
          ) : (
            <>
              <Sparkles size={16} />
              {output ? 'Regenerate' : 'Generate Draft'}
            </>
          )}
        </Button>

        {!lead && <div className="text-muted text-xs text-center">Select a lead to begin.</div>}
      </div>

      {error && (
        <div className="card p-3 border-bad/40 text-bad text-sm">{error}</div>
      )}

      {(isGenerating || output) && (
        <div className="card p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
              Draft
            </div>
            {output && !isGenerating && <CopyButton text={output} />}
          </div>
          {isGenerating ? (
            <div className="caos-pulse text-ink text-sm">Generating…</div>
          ) : (
            <pre className="whitespace-pre-wrap text-ink text-[14px] leading-relaxed font-sans">
              {output}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}

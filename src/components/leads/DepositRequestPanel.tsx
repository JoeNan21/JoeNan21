import { useEffect } from 'react'
import { X, Copy, RefreshCw, Sparkles } from 'lucide-react'
import type { Lead, MessageType } from '@/types'
import { EVENT_LABEL, ROOM_LABEL } from '@/types'
import { Button } from '@/components/ui/Button'
import { useClaude } from '@/hooks/useClaude'
import { useSettingsStore } from '@/store/LeadsContext'
import { buildMessagePrompt } from '@/lib/claude'
import { formatNZDate } from '@/lib/dates'

interface Props {
  lead: Lead
  messageType: 'deposit-request' | 'date-hold'
  onClose: () => void
  onCopy: (text: string) => void
}

export function DepositRequestPanel({ lead, messageType, onClose, onCopy }: Props) {
  const { settings } = useSettingsStore()
  const claude = useClaude(settings.apiKey)

  useEffect(() => {
    claude.generate(buildMessagePrompt(lead, messageType as MessageType, ''), 300)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleCopy = async () => {
    if (!claude.output) return
    try {
      await navigator.clipboard.writeText(claude.output)
    } catch {
      // clipboard unavailable — still fire onCopy so note is appended
    }
    onCopy(claude.output)
    onClose()
  }

  const pills = [
    lead.eventType && EVENT_LABEL[lead.eventType],
    lead.room && ROOM_LABEL[lead.room],
    lead.eventDate && formatNZDate(lead.eventDate),
    lead.guestCount && `${lead.guestCount} pax`,
    lead.estimatedValue && `$${lead.estimatedValue.toLocaleString()}`,
  ].filter(Boolean) as string[]

  return (
    <div className="rounded border border-gold/30 bg-elevated p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-[11px] uppercase tracking-wider text-gold font-semibold">
          {messageType === 'deposit-request' ? 'Deposit Request' : 'Date Hold Offer'}
        </div>
        <button onClick={onClose} className="text-muted hover:text-ink transition-colors p-1">
          <X size={14} />
        </button>
      </div>

      {pills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {pills.map((p) => (
            <span
              key={p}
              className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] bg-surface border border-line text-muted"
            >
              {p}
            </span>
          ))}
        </div>
      )}

      <div className="min-h-[80px]">
        {claude.isGenerating ? (
          <div className="caos-pulse text-ink text-sm">Generating…</div>
        ) : claude.error ? (
          <div className="text-bad text-sm">{claude.error}</div>
        ) : claude.output ? (
          <div className="text-ink text-sm whitespace-pre-wrap leading-relaxed">{claude.output}</div>
        ) : null}
      </div>

      <div className="flex items-center justify-between gap-2 pt-1">
        <button
          onClick={() => claude.generate(buildMessagePrompt(lead, messageType as MessageType, ''), 300)}
          disabled={claude.isGenerating}
          className="text-muted text-xs hover:text-gold transition-colors disabled:opacity-40 flex items-center gap-1"
        >
          <RefreshCw size={12} /> Regenerate
        </button>
        <div className="flex gap-2">
          <Button
            variant="gold"
            onClick={handleCopy}
            disabled={!claude.output || claude.isGenerating}
          >
            <Copy size={14} /> Copy &amp; Log
            <Sparkles size={12} className="opacity-60" />
          </Button>
        </div>
      </div>
    </div>
  )
}

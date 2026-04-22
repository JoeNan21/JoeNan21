import type { Lead } from '@/types'
import { EVENT_LABEL, ROOM_LABEL } from '@/types'
import { Pill } from '@/components/ui/Pill'
import { Dot } from '@/components/ui/Dot'
import { formatShortDate, gapColour, gapLabel, hoursSince } from '@/lib/dates'
import { cn } from '@/lib/cn'

const eventTone: Record<Lead['eventType'], 'gold' | 'teal' | 'muted'> = {
  wedding: 'gold',
  corporate: 'teal',
  funeral: 'muted',
  cultural: 'gold',
  private: 'teal',
}

export function LeadCard({
  lead,
  onClick,
  dragHandleProps,
  dragging,
  compact,
}: {
  lead: Lead
  onClick?: () => void
  dragHandleProps?: Record<string, unknown>
  dragging?: boolean
  compact?: boolean
}) {
  const gap = hoursSince(lead.lastContact)
  const tone = gapColour(gap)

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left card p-3 hover:border-gold/50 transition-colors',
        dragging && 'opacity-50 border-gold',
      )}
      {...(dragHandleProps ?? {})}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="text-ink text-sm font-semibold truncate">{lead.name}</div>
          <div className="text-muted text-[11px] mt-0.5">
            {formatShortDate(lead.eventDate)}
            {lead.guestCount ? ` · ${lead.guestCount} pax` : ''}
          </div>
        </div>
        <Pill tone={eventTone[lead.eventType]}>{EVENT_LABEL[lead.eventType]}</Pill>
      </div>

      {!compact && (
        <div className="flex items-center justify-between gap-2 mt-3 text-[11px]">
          <div className="flex items-center gap-1.5 text-muted">
            <Dot tone={tone} />
            <span className={cn(tone === 'bad' && 'text-bad', tone === 'warn' && 'text-warn')}>
              {gapLabel(gap)}
            </span>
          </div>
          <div className="text-ink font-medium">
            {lead.estimatedValue ? `$${(lead.estimatedValue / 1000).toFixed(1)}k` : '—'}
          </div>
        </div>
      )}

      {!compact && lead.room && (
        <div className="text-[10px] text-muted mt-1 uppercase tracking-wide">
          {ROOM_LABEL[lead.room]}
        </div>
      )}
    </button>
  )
}

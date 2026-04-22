import type { Lead } from '@/types'
import { EVENT_LABEL, STAGE_LABEL } from '@/types'
import { Pill } from '@/components/ui/Pill'
import { Dot } from '@/components/ui/Dot'
import { formatShortDate, gapColour, gapLabel, hoursSince } from '@/lib/dates'

export function ListView({
  leads,
  onOpenLead,
}: {
  leads: Lead[]
  onOpenLead: (lead: Lead) => void
}) {
  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-[10px] uppercase tracking-wider text-muted border-b border-line">
              <th className="text-left px-3 py-2 font-medium">Lead</th>
              <th className="text-left px-3 py-2 font-medium hidden md:table-cell">Event</th>
              <th className="text-left px-3 py-2 font-medium">Stage</th>
              <th className="text-left px-3 py-2 font-medium hidden md:table-cell">Event Date</th>
              <th className="text-right px-3 py-2 font-medium hidden sm:table-cell">Value</th>
              <th className="text-left px-3 py-2 font-medium">Last Contact</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((lead) => {
              const gap = hoursSince(lead.lastContact)
              const tone = gapColour(gap)
              return (
                <tr
                  key={lead.id}
                  onClick={() => onOpenLead(lead)}
                  className="border-b border-line/60 hover:bg-gold/5 cursor-pointer transition-colors"
                >
                  <td className="px-3 py-3">
                    <div className="text-ink font-medium">{lead.name}</div>
                    <div className="text-muted text-[11px] md:hidden mt-0.5">
                      {EVENT_LABEL[lead.eventType]} · {formatShortDate(lead.eventDate)}
                    </div>
                  </td>
                  <td className="px-3 py-3 hidden md:table-cell">
                    <Pill tone="muted">{EVENT_LABEL[lead.eventType]}</Pill>
                  </td>
                  <td className="px-3 py-3">
                    <Pill
                      tone={
                        lead.stage === 'confirmed'
                          ? 'ok'
                          : lead.stage === 'lost'
                            ? 'bad'
                            : lead.stage === 'post-visit' || lead.stage === 'visit-booked'
                              ? 'gold'
                              : 'muted'
                      }
                    >
                      {STAGE_LABEL[lead.stage]}
                    </Pill>
                  </td>
                  <td className="px-3 py-3 hidden md:table-cell text-muted">
                    {formatShortDate(lead.eventDate)}
                  </td>
                  <td className="px-3 py-3 text-right hidden sm:table-cell text-ink">
                    {lead.estimatedValue ? `$${lead.estimatedValue.toLocaleString()}` : '—'}
                  </td>
                  <td className="px-3 py-3">
                    <div className="inline-flex items-center gap-1.5 text-[12px]">
                      <Dot tone={tone} />
                      <span
                        className={
                          tone === 'bad' ? 'text-bad' : tone === 'warn' ? 'text-warn' : 'text-muted'
                        }
                      >
                        {gapLabel(gap)}
                      </span>
                    </div>
                  </td>
                </tr>
              )
            })}
            {leads.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-center text-muted text-sm">
                  No leads match. Clear filters or add a new lead.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

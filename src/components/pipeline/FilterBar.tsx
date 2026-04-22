import { Search } from 'lucide-react'
import type { EventType, Stage } from '@/types'
import { EVENT_LABEL, STAGE_LABEL, STAGE_ORDER } from '@/types'

export interface Filters {
  eventTypes: EventType[]
  stages: Stage[]
  overdueOnly: boolean
  search: string
}

export function FilterBar({
  filters,
  onChange,
}: {
  filters: Filters
  onChange: (f: Filters) => void
}) {
  const toggleType = (t: EventType) => {
    const has = filters.eventTypes.includes(t)
    onChange({
      ...filters,
      eventTypes: has ? filters.eventTypes.filter((x) => x !== t) : [...filters.eventTypes, t],
    })
  }
  const toggleStage = (s: Stage) => {
    const has = filters.stages.includes(s)
    onChange({
      ...filters,
      stages: has ? filters.stages.filter((x) => x !== s) : [...filters.stages, s],
    })
  }
  return (
    <div className="space-y-2">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
        <input
          className="input pl-9"
          placeholder="Search name, source, notes…"
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
        />
      </div>
      <div className="flex flex-wrap gap-1.5">
        {(Object.keys(EVENT_LABEL) as EventType[]).map((t) => {
          const active = filters.eventTypes.includes(t)
          return (
            <button
              key={t}
              onClick={() => toggleType(t)}
              className={`px-3 py-1.5 text-[11px] uppercase tracking-wider rounded border transition-colors ${
                active ? 'bg-gold text-black border-gold' : 'border-line text-muted hover:text-ink'
              }`}
            >
              {EVENT_LABEL[t]}
            </button>
          )
        })}
        <div className="w-px bg-line mx-1" />
        {STAGE_ORDER.map((s) => {
          const active = filters.stages.includes(s)
          return (
            <button
              key={s}
              onClick={() => toggleStage(s)}
              className={`px-3 py-1.5 text-[11px] uppercase tracking-wider rounded border transition-colors ${
                active ? 'bg-teal text-ink border-teal' : 'border-line text-muted hover:text-ink'
              }`}
            >
              {STAGE_LABEL[s]}
            </button>
          )
        })}
        <div className="w-px bg-line mx-1" />
        <button
          onClick={() => onChange({ ...filters, overdueOnly: !filters.overdueOnly })}
          className={`px-3 py-1.5 text-[11px] uppercase tracking-wider rounded border transition-colors ${
            filters.overdueOnly ? 'bg-bad text-ink border-bad' : 'border-line text-muted hover:text-ink'
          }`}
        >
          Overdue Only
        </button>
      </div>
    </div>
  )
}

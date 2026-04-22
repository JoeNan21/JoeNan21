import { useMemo, useState } from 'react'
import { Plus, LayoutGrid, List } from 'lucide-react'
import { useLeadsStore } from '@/store/LeadsContext'
import { Button } from '@/components/ui/Button'
import { Drawer } from '@/components/ui/Drawer'
import { KanbanView } from '@/components/pipeline/KanbanView'
import { ListView } from '@/components/pipeline/ListView'
import { FilterBar, type Filters } from '@/components/pipeline/FilterBar'
import { LeadForm } from '@/components/leads/LeadForm'
import { LeadDetail } from '@/components/leads/LeadDetail'
import { isOverdueNew, isOverduePostVisit } from '@/lib/priority'
import type { Lead } from '@/types'

const DEFAULT_FILTERS: Filters = {
  eventTypes: [],
  stages: [],
  overdueOnly: false,
  search: '',
}

export function PipelinePage() {
  const { leads, setStage, create } = useLeadsStore()
  const [view, setView] = useState<'kanban' | 'list'>('kanban')
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS)
  const [openLead, setOpenLead] = useState<Lead | null>(null)
  const [addOpen, setAddOpen] = useState(false)

  const filtered = useMemo(() => {
    const q = filters.search.trim().toLowerCase()
    return leads.filter((l) => {
      if (filters.eventTypes.length && !filters.eventTypes.includes(l.eventType)) return false
      if (filters.stages.length && !filters.stages.includes(l.stage)) return false
      if (filters.overdueOnly && !(isOverdueNew(l) || isOverduePostVisit(l))) return false
      if (q) {
        const blob = `${l.name} ${l.source} ${l.notes}`.toLowerCase()
        if (!blob.includes(q)) return false
      }
      return true
    })
  }, [leads, filters])

  // keep openLead fresh if underlying data changes
  const freshOpen = openLead ? leads.find((l) => l.id === openLead.id) ?? null : null

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-ink">Pipeline</h1>
          <div className="text-muted text-xs mt-0.5">
            {filtered.length} of {leads.length} leads
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex rounded border border-line overflow-hidden">
            <button
              onClick={() => setView('kanban')}
              className={`px-3 h-10 flex items-center gap-1.5 text-xs ${view === 'kanban' ? 'bg-gold text-black' : 'text-muted hover:text-ink'}`}
            >
              <LayoutGrid size={14} /> Kanban
            </button>
            <button
              onClick={() => setView('list')}
              className={`px-3 h-10 flex items-center gap-1.5 text-xs ${view === 'list' ? 'bg-gold text-black' : 'text-muted hover:text-ink'}`}
            >
              <List size={14} /> List
            </button>
          </div>
          <Button onClick={() => setAddOpen(true)}>
            <Plus size={16} /> Add Lead
          </Button>
        </div>
      </div>

      <FilterBar filters={filters} onChange={setFilters} />

      <div className="sm:hidden flex rounded border border-line overflow-hidden w-full">
        <button
          onClick={() => setView('kanban')}
          className={`flex-1 h-10 flex items-center justify-center gap-1.5 text-xs ${view === 'kanban' ? 'bg-gold text-black' : 'text-muted'}`}
        >
          <LayoutGrid size={14} /> Kanban
        </button>
        <button
          onClick={() => setView('list')}
          className={`flex-1 h-10 flex items-center justify-center gap-1.5 text-xs ${view === 'list' ? 'bg-gold text-black' : 'text-muted'}`}
        >
          <List size={14} /> List
        </button>
      </div>

      {view === 'kanban' ? (
        <KanbanView
          leads={filtered}
          onOpenLead={setOpenLead}
          onMoveStage={(id, stage) => setStage(id, stage)}
        />
      ) : (
        <ListView leads={filtered} onOpenLead={setOpenLead} />
      )}

      <Drawer open={addOpen} onClose={() => setAddOpen(false)} title="New Lead" wide>
        <LeadForm
          onSubmit={(values) => {
            create(values)
            setAddOpen(false)
          }}
        />
      </Drawer>

      <LeadDetail lead={freshOpen} open={!!openLead} onClose={() => setOpenLead(null)} />
    </div>
  )
}

import { useMemo } from 'react'
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  closestCenter,
  useDraggable,
  useDroppable,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { useState } from 'react'
import type { Lead, Stage } from '@/types'
import { STAGE_LABEL, STAGE_ORDER } from '@/types'
import { LeadCard } from '@/components/leads/LeadCard'
import { Pill } from '@/components/ui/Pill'

export function KanbanView({
  leads,
  onOpenLead,
  onMoveStage,
}: {
  leads: Lead[]
  onOpenLead: (lead: Lead) => void
  onMoveStage: (id: string, stage: Stage) => void
}) {
  const [activeId, setActiveId] = useState<string | null>(null)
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 200, tolerance: 8 } }),
  )

  const byStage = useMemo(() => {
    const groups: Record<Stage, Lead[]> = {
      new: [],
      contacted: [],
      'visit-booked': [],
      'post-visit': [],
      confirmed: [],
      lost: [],
    }
    for (const lead of leads) groups[lead.stage].push(lead)
    return groups
  }, [leads])

  const active = useMemo(() => leads.find((l) => l.id === activeId) ?? null, [activeId, leads])

  const onDragStart = (e: DragStartEvent) => setActiveId(String(e.active.id))
  const onDragEnd = (e: DragEndEvent) => {
    setActiveId(null)
    if (!e.over) return
    const target = String(e.over.id) as Stage
    const id = String(e.active.id)
    const lead = leads.find((l) => l.id === id)
    if (lead && lead.stage !== target) onMoveStage(id, target)
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
    >
      <div className="flex gap-3 overflow-x-auto snap-x-mandatory pb-3 -mx-3 px-3 md:mx-0 md:px-0">
        {STAGE_ORDER.map((stage) => (
          <Column
            key={stage}
            stage={stage}
            leads={byStage[stage]}
            onOpenLead={onOpenLead}
          />
        ))}
      </div>
      <DragOverlay>
        {active && <LeadCard lead={active} compact />}
      </DragOverlay>
    </DndContext>
  )
}

function Column({
  stage,
  leads,
  onOpenLead,
}: {
  stage: Stage
  leads: Lead[]
  onOpenLead: (lead: Lead) => void
}) {
  const { setNodeRef, isOver } = useDroppable({ id: stage })
  const total = leads.reduce((s, l) => s + (l.estimatedValue ?? 0), 0)

  return (
    <div
      ref={setNodeRef}
      className={`snap-col flex-shrink-0 w-[280px] md:w-[260px] flex flex-col rounded border bg-surface/60 transition-colors ${
        isOver ? 'border-gold bg-gold/5' : 'border-line'
      }`}
    >
      <div className="px-3 py-2.5 border-b border-line flex items-center justify-between flex-shrink-0">
        <div>
          <div className="text-ink text-sm font-semibold">{STAGE_LABEL[stage]}</div>
          <div className="text-[10px] text-muted uppercase tracking-wider mt-0.5">
            {leads.length} lead{leads.length === 1 ? '' : 's'}
            {total > 0 && ` · $${(total / 1000).toFixed(1)}k`}
          </div>
        </div>
        <Pill tone={stage === 'confirmed' ? 'ok' : stage === 'lost' ? 'bad' : 'muted'}>
          {leads.length}
        </Pill>
      </div>
      <div className="p-2 space-y-2 flex-1 min-h-[200px]">
        {leads.length === 0 ? (
          <div className="text-[11px] text-muted text-center py-6 px-2 leading-relaxed">
            Drop here to move to {STAGE_LABEL[stage].toLowerCase()}
          </div>
        ) : (
          leads.map((lead) => (
            <DraggableCard key={lead.id} lead={lead} onOpenLead={onOpenLead} />
          ))
        )}
      </div>
    </div>
  )
}

function DraggableCard({
  lead,
  onOpenLead,
}: {
  lead: Lead
  onOpenLead: (lead: Lead) => void
}) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({ id: lead.id })
  return (
    <div
      ref={setNodeRef}
      style={{ touchAction: 'none' }}
      {...attributes}
      {...listeners}
      onClick={() => onOpenLead(lead)}
    >
      <LeadCard lead={lead} dragging={isDragging} />
    </div>
  )
}

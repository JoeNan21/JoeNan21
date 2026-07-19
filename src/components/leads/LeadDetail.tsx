import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CalendarPlus,
  CheckCircle2,
  Mail,
  MessageSquarePlus,
  Notebook,
  Phone,
  Trash2,
  Wrench,
  XCircle,
} from 'lucide-react'
import type { Lead, Stage } from '@/types'
import { EVENT_LABEL, ROOM_LABEL, STAGE_LABEL, STAGE_ORDER } from '@/types'
import { Drawer } from '@/components/ui/Drawer'
import { Pill } from '@/components/ui/Pill'
import { Dot } from '@/components/ui/Dot'
import { Button } from '@/components/ui/Button'
import { useLeadsStore } from '@/store/LeadsContext'
import { DepositRequestPanel } from '@/components/leads/DepositRequestPanel'
import {
  formatNZDate,
  gapColour,
  gapLabel,
  hoursSince,
  isoDateOnly,
  todayISO,
} from '@/lib/dates'

const eventTone: Record<Lead['eventType'], 'gold' | 'teal' | 'muted'> = {
  wedding: 'gold',
  corporate: 'teal',
  funeral: 'muted',
  cultural: 'gold',
  private: 'teal',
}

export function LeadDetail({
  lead,
  open,
  onClose,
}: {
  lead: Lead | null
  open: boolean
  onClose: () => void
}) {
  const navigate = useNavigate()
  const { setStage, update, appendNote, logContact, remove } = useLeadsStore()
  const [note, setNote] = useState('')
  const [confirming, setConfirming] = useState<'lost' | 'delete' | null>(null)
  const [depositPanel, setDepositPanel] = useState<'deposit-request' | 'date-hold' | null>(null)

  useEffect(() => {
    if (!open) setDepositPanel(null)
  }, [open])

  const gap = useMemo(() => (lead ? hoursSince(lead.lastContact) : null), [lead])

  if (!lead) return null

  const tone = gapColour(gap)
  const gapText = gapLabel(gap)

  const go = (path: string) => {
    onClose()
    navigate(path)
  }

  const handleStageChange = (next: Stage) => {
    if (next === 'lost') {
      setConfirming('lost')
      return
    }
    if (next === 'confirmed') {
      const val = prompt(
        'Deposit amount received (NZD):',
        lead.estimatedValue ? String(lead.estimatedValue) : '',
      )
      if (val == null) return
      const amount = Number(val)
      if (!Number.isFinite(amount)) return
      update(lead.id, {
        stage: 'confirmed',
        depositAmount: amount,
        depositReceived: true,
      })
      return
    }
    setStage(lead.id, next)
  }

  const handleBookVisit = () => {
    const today = isoDateOnly(todayISO())
    const val = prompt('Visit date (YYYY-MM-DD):', today)
    if (!val) return
    const iso = new Date(val + 'T10:00:00').toISOString()
    update(lead.id, { visitDate: iso, stage: 'visit-booked' })
  }

  const handleAddNote = () => {
    if (!note.trim()) return
    appendNote(lead.id, note)
    setNote('')
  }

  return (
    <Drawer open={open} onClose={onClose} title="Lead" wide>
      <div className="space-y-5">
        {/* Header */}
        <div>
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="text-ink text-lg font-semibold leading-tight">{lead.name}</h3>
              <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                <Pill tone={eventTone[lead.eventType]}>{EVENT_LABEL[lead.eventType]}</Pill>
                <Pill tone="muted">{STAGE_LABEL[lead.stage]}</Pill>
                <span className="inline-flex items-center gap-1.5 text-[11px] text-muted">
                  <Dot tone={tone} />
                  <span className={tone === 'bad' ? 'text-bad' : tone === 'warn' ? 'text-warn' : ''}>
                    {gapText}
                  </span>
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-[10px] uppercase tracking-wider text-muted">Est. Value</div>
              <div className="text-gold text-lg font-semibold">
                {lead.estimatedValue ? `$${lead.estimatedValue.toLocaleString()}` : '—'}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions or Close Panel */}
        {lead.stage === 'post-visit' ? (
          <div
            className="rounded border-l-4 p-4 space-y-3"
            style={{ backgroundColor: 'rgba(124,29,29,0.25)', borderLeftColor: '#ef4444' }}
          >
            <div className="text-[11px] uppercase tracking-wider font-semibold" style={{ color: '#ef4444' }}>
              Close or Park
            </div>
            <div className="space-y-2">
              <Button variant="gold" className="w-full" onClick={() => setDepositPanel('deposit-request')}>
                Request Deposit
              </Button>
              <Button variant="teal" className="w-full" onClick={() => setDepositPanel('date-hold')}>
                Offer Date Hold
              </Button>
              <Button variant="ghost" className="w-full" onClick={() => setConfirming('lost')}>
                Mark Lost
              </Button>
            </div>
            {depositPanel && (
              <DepositRequestPanel
                lead={lead}
                messageType={depositPanel}
                onClose={() => setDepositPanel(null)}
                onCopy={(text) => {
                  appendNote(lead.id, `Sent ${depositPanel === 'deposit-request' ? 'deposit request' : 'date hold offer'}: ${text.slice(0, 80)}…`)
                }}
              />
            )}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            <Button variant="gold" onClick={() => go(`/composer?leadId=${lead.id}`)}>
              <Mail size={16} /> Draft Message
            </Button>
            <Button variant="teal" onClick={handleBookVisit}>
              <CalendarPlus size={16} /> Book Visit
            </Button>
            <Button variant="ghost" onClick={() => logContact(lead.id)}>
              <Phone size={16} /> Log Contact
            </Button>
            <Button variant="ghost" onClick={() => go(`/tools?leadId=${lead.id}&tab=prep`)}>
              <Wrench size={16} /> Prep Me
            </Button>
            <Button variant="ghost" onClick={() => go(`/tools?leadId=${lead.id}&tab=summary`)}>
              <Notebook size={16} /> Process Notes
            </Button>
            {lead.stage !== 'confirmed' && (
              <Button variant="ghost" onClick={() => handleStageChange('confirmed')}>
                <CheckCircle2 size={16} /> Mark Confirmed
              </Button>
            )}
          </div>
        )}

        {/* Stage mover */}
        <div>
          <div className="label">Stage</div>
          <div className="flex flex-wrap gap-1.5">
            {STAGE_ORDER.map((s) => {
              const active = s === lead.stage
              return (
                <button
                  key={s}
                  onClick={() => handleStageChange(s)}
                  className={`px-3 py-2 text-[11px] uppercase tracking-wider rounded border transition-colors ${
                    active
                      ? 'bg-gold text-black border-gold'
                      : s === 'lost'
                        ? 'border-line text-bad hover:border-bad'
                        : 'border-line text-muted hover:text-gold hover:border-gold'
                  }`}
                  style={{ minHeight: 40 }}
                >
                  {STAGE_LABEL[s]}
                </button>
              )
            })}
          </div>
        </div>

        {/* Fields */}
        <div className="grid grid-cols-2 gap-3">
          <Field label="Event Date">
            <input
              type="date"
              className="input"
              value={lead.eventDate ?? ''}
              onChange={(e) => update(lead.id, { eventDate: e.target.value || null })}
            />
          </Field>
          <Field label="Guest Count">
            <input
              type="number"
              className="input"
              value={lead.guestCount ?? ''}
              onChange={(e) =>
                update(lead.id, {
                  guestCount: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </Field>
          <Field label="Est. Value">
            <input
              type="number"
              className="input"
              value={lead.estimatedValue ?? ''}
              onChange={(e) =>
                update(lead.id, {
                  estimatedValue: e.target.value ? Number(e.target.value) : null,
                })
              }
            />
          </Field>
          <Field label="Room">
            <select
              className="input"
              value={lead.room ?? ''}
              onChange={(e) => update(lead.id, { room: (e.target.value || null) as Lead['room'] })}
            >
              <option value="">— none —</option>
              {Object.entries(ROOM_LABEL).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Visit Date">
            <div className="text-ink text-sm py-2">{formatNZDate(lead.visitDate)}</div>
          </Field>
          <Field label="Enquired">
            <div className="text-ink text-sm py-2">{formatNZDate(lead.enquiryDate)}</div>
          </Field>
        </div>

        {/* Competing venues */}
        <div>
          <div className="label">Competing Venues</div>
          <input
            className="input"
            placeholder="comma separated"
            value={lead.competingVenues.join(', ')}
            onChange={(e) =>
              update(lead.id, {
                competingVenues: e.target.value
                  .split(',')
                  .map((s) => s.trim())
                  .filter(Boolean),
              })
            }
          />
        </div>

        {/* Notes */}
        <div>
          <div className="label">Interaction Log</div>
          <pre className="whitespace-pre-wrap text-[12px] text-muted bg-elevated border border-line rounded p-3 max-h-48 overflow-y-auto leading-relaxed">
            {lead.notes || '— no notes yet —'}
          </pre>
          <div className="mt-2 flex gap-2">
            <input
              className="input flex-1"
              placeholder="Add note — will timestamp and update last contact"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleAddNote()
              }}
            />
            <Button variant="ghost" onClick={handleAddNote}>
              <MessageSquarePlus size={16} /> Add
            </Button>
          </div>
        </div>

        {/* Destructive */}
        <div className="pt-3 border-t border-line flex gap-2">
          <Button variant="danger" onClick={() => setConfirming('delete')}>
            <Trash2 size={16} /> Delete Lead
          </Button>
        </div>
      </div>

      {confirming && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/70 p-4">
          <div className="card p-5 max-w-sm w-full">
            <div className="flex items-start gap-2 mb-3">
              <XCircle className="text-bad flex-shrink-0 mt-0.5" size={18} />
              <div>
                <div className="text-ink font-semibold text-sm">
                  {confirming === 'lost' ? 'Mark as Lost?' : 'Delete Lead?'}
                </div>
                <div className="text-muted text-xs mt-1">
                  {confirming === 'lost'
                    ? 'This lead will stop appearing in active pipeline metrics.'
                    : 'This permanently removes the lead and all notes.'}
                </div>
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="ghost" onClick={() => setConfirming(null)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => {
                  if (confirming === 'lost') {
                    setStage(lead.id, 'lost')
                  } else {
                    remove(lead.id)
                  }
                  setConfirming(null)
                  onClose()
                }}
              >
                {confirming === 'lost' ? 'Mark Lost' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </Drawer>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="label">{label}</div>
      {children}
    </div>
  )
}

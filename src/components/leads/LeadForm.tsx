import { useState } from 'react'
import type { ContactMethod, EventType, Lead, Room, Stage } from '@/types'
import { Button } from '@/components/ui/Button'

const EVENT_OPTIONS: { value: EventType; label: string }[] = [
  { value: 'wedding', label: 'Wedding' },
  { value: 'corporate', label: 'Corporate' },
  { value: 'funeral', label: 'Funeral / Unveiling' },
  { value: 'cultural', label: 'Cultural' },
  { value: 'private', label: 'Private' },
]

const CONTACT_OPTIONS: ContactMethod[] = ['email', 'phone', 'social', 'referral', 'walk-in']
const ROOM_OPTIONS: Room[] = [null, 'pohutukawa', 'manukau', 'somerset']
const STAGE_OPTIONS: Stage[] = ['new', 'contacted', 'visit-booked', 'post-visit', 'confirmed', 'lost']

export function LeadForm({
  initial,
  onSubmit,
  submitLabel = 'Create Lead',
}: {
  initial?: Partial<Lead>
  onSubmit: (values: Partial<Lead> & { name: string }) => void
  submitLabel?: string
}) {
  const [name, setName] = useState(initial?.name ?? '')
  const [eventType, setEventType] = useState<EventType>(initial?.eventType ?? 'wedding')
  const [eventDate, setEventDate] = useState(initial?.eventDate ?? '')
  const [guestCount, setGuestCount] = useState(
    initial?.guestCount != null ? String(initial.guestCount) : '',
  )
  const [estimatedValue, setEstimatedValue] = useState(
    initial?.estimatedValue != null ? String(initial.estimatedValue) : '',
  )
  const [contactMethod, setContactMethod] = useState<ContactMethod>(
    initial?.contactMethod ?? 'email',
  )
  const [source, setSource] = useState(initial?.source ?? '')
  const [room, setRoom] = useState<Room>(initial?.room ?? null)
  const [stage, setStage] = useState<Stage>(initial?.stage ?? 'new')
  const [competing, setCompeting] = useState((initial?.competingVenues ?? []).join(', '))
  const [notes, setNotes] = useState(initial?.notes ?? '')

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    onSubmit({
      name: name.trim(),
      eventType,
      eventDate: eventDate || null,
      guestCount: guestCount ? Number(guestCount) : null,
      estimatedValue: estimatedValue ? Number(estimatedValue) : null,
      contactMethod,
      source: source.trim(),
      room,
      stage,
      competingVenues: competing
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      notes: notes.trim(),
    })
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <div>
        <label className="label">Lead Name</label>
        <input
          className="input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Sarah & Tom Henderson"
          required
          autoFocus
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">Event Type</label>
          <select
            className="input"
            value={eventType}
            onChange={(e) => setEventType(e.target.value as EventType)}
          >
            {EVENT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">Stage</label>
          <select
            className="input"
            value={stage}
            onChange={(e) => setStage(e.target.value as Stage)}
          >
            {STAGE_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">Event Date</label>
          <input
            type="date"
            className="input"
            value={eventDate ?? ''}
            onChange={(e) => setEventDate(e.target.value)}
          />
        </div>
        <div>
          <label className="label">Guest Count</label>
          <input
            type="number"
            min={1}
            className="input"
            value={guestCount}
            onChange={(e) => setGuestCount(e.target.value)}
            placeholder="e.g. 120"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">Est. Value (NZD)</label>
          <input
            type="number"
            min={0}
            step={100}
            className="input"
            value={estimatedValue}
            onChange={(e) => setEstimatedValue(e.target.value)}
            placeholder="e.g. 15000"
          />
        </div>
        <div>
          <label className="label">Room</label>
          <select
            className="input"
            value={room ?? ''}
            onChange={(e) => setRoom((e.target.value || null) as Room)}
          >
            {ROOM_OPTIONS.map((r) => (
              <option key={r ?? 'none'} value={r ?? ''}>
                {r ? r[0].toUpperCase() + r.slice(1) : '— Not assigned —'}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">Contact Method</label>
          <select
            className="input"
            value={contactMethod}
            onChange={(e) => setContactMethod(e.target.value as ContactMethod)}
          >
            {CONTACT_OPTIONS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label">Source</label>
          <input
            className="input"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Google, Referral, LinkedIn…"
          />
        </div>
      </div>

      <div>
        <label className="label">Competing Venues (comma separated)</label>
        <input
          className="input"
          value={competing}
          onChange={(e) => setCompeting(e.target.value)}
          placeholder="Wintergarden, Cordis…"
        />
      </div>

      <div>
        <label className="label">Notes</label>
        <textarea
          className="textarea"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={4}
          placeholder="Key context, vision, objections…"
        />
      </div>

      <Button type="submit" full>
        {submitLabel}
      </Button>
    </form>
  )
}

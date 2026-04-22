import { useMemo, useState } from 'react'
import { Eye, EyeOff, Plus, Trash2 } from 'lucide-react'
import { useSettingsStore } from '@/store/LeadsContext'
import { maskKey } from '@/hooks/useSettings'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'
import { ROOM_LABEL } from '@/types'
import type { Room } from '@/types'
import { monthLabel } from '@/lib/dates'

function genId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`
}

function nextMonths(n: number): string[] {
  const out: string[] = []
  const d = new Date()
  d.setDate(1)
  for (let i = 0; i < n; i++) {
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    out.push(key)
    d.setMonth(d.getMonth() + 1)
  }
  return out
}

export function SettingsPage() {
  const { settings, update, setTarget, addRoomBlock, removeRoomBlock } = useSettingsStore()
  const [editingKey, setEditingKey] = useState(!settings.apiKey)
  const [tempKey, setTempKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [blockRoom, setBlockRoom] = useState<Room>('pohutukawa')
  const [blockDate, setBlockDate] = useState('')
  const [blockReason, setBlockReason] = useState('')

  const months = useMemo(() => nextMonths(6), [])

  const saveKey = () => {
    update({ apiKey: tempKey.trim() })
    setTempKey('')
    setEditingKey(false)
  }

  const addBlock = () => {
    if (!blockDate || !blockRoom) return
    addRoomBlock({
      id: genId(),
      room: blockRoom,
      date: blockDate,
      reason: blockReason.trim() || 'blocked',
    })
    setBlockDate('')
    setBlockReason('')
  }

  return (
    <div className="p-4 md:p-6 space-y-5 max-w-2xl mx-auto">
      <div>
        <h1 className="text-xl md:text-2xl font-semibold text-ink">Settings</h1>
        <div className="text-muted text-xs mt-0.5">
          Operator, venue, API key, revenue targets, room blocks.
        </div>
      </div>

      <div className="card p-4 space-y-3">
        <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
          Operator
        </div>
        <div>
          <label className="label">Operator Name</label>
          <input
            className="input"
            value={settings.operatorName}
            onChange={(e) => update({ operatorName: e.target.value })}
          />
        </div>
        <div>
          <label className="label">Venue Name</label>
          <input
            className="input"
            value={settings.venueName}
            onChange={(e) => update({ venueName: e.target.value })}
          />
        </div>
      </div>

      <div className="card p-4 space-y-3">
        <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
          Claude API Key
        </div>
        {!editingKey && settings.apiKey ? (
          <div className="flex items-center justify-between gap-2">
            <div className="font-mono text-sm text-ink">
              {showKey ? settings.apiKey : maskKey(settings.apiKey)}
            </div>
            <div className="flex gap-1">
              <button
                className="btn-icon"
                onClick={() => setShowKey((s) => !s)}
                aria-label={showKey ? 'Hide key' : 'Show key'}
              >
                {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
              <Button variant="ghost" onClick={() => setEditingKey(true)}>
                Change
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <input
              className="input font-mono"
              placeholder="sk-ant-…"
              value={tempKey}
              onChange={(e) => setTempKey(e.target.value)}
              type="password"
              autoFocus
            />
            <div className="flex gap-2">
              <Button onClick={saveKey} disabled={!tempKey.trim()}>
                Save Key
              </Button>
              {settings.apiKey && (
                <Button variant="ghost" onClick={() => setEditingKey(false)}>
                  Cancel
                </Button>
              )}
            </div>
            <div className="text-muted text-[11px] leading-relaxed">
              Stored in localStorage only. Never sent anywhere other than api.anthropic.com.
            </div>
          </div>
        )}
      </div>

      <div className="card p-4 space-y-3">
        <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
          Monthly Revenue Targets
        </div>
        <div className="space-y-2">
          {months.map((key) => (
            <div key={key} className="flex items-center gap-2">
              <div className="w-28 text-sm text-ink">{monthLabel(key)}</div>
              <div className="flex-1 relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-sm">
                  $
                </span>
                <input
                  type="number"
                  min={0}
                  step={500}
                  className="input pl-6"
                  placeholder="0"
                  value={settings.monthlyTargets[key] ?? ''}
                  onChange={(e) =>
                    setTarget(key, e.target.value ? Number(e.target.value) : 0)
                  }
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-4 space-y-3">
        <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
          Room Availability Blocks
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="label">Room</label>
            <select
              className="input"
              value={blockRoom ?? ''}
              onChange={(e) => setBlockRoom((e.target.value || null) as Room)}
            >
              {Object.entries(ROOM_LABEL).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Date</label>
            <input
              type="date"
              className="input"
              value={blockDate}
              onChange={(e) => setBlockDate(e.target.value)}
            />
          </div>
        </div>
        <div>
          <label className="label">Reason</label>
          <input
            className="input"
            value={blockReason}
            onChange={(e) => setBlockReason(e.target.value)}
            placeholder="e.g. Maintenance, private hire"
          />
        </div>
        <Button variant="ghost" onClick={addBlock} disabled={!blockDate}>
          <Plus size={16} /> Add Block
        </Button>

        {settings.roomBlocks.length > 0 && (
          <div className="space-y-1.5 pt-2">
            {settings.roomBlocks.map((b) => (
              <div
                key={b.id}
                className="flex items-center justify-between gap-2 text-sm border-t border-line pt-2"
              >
                <div className="flex items-center gap-2">
                  <Pill tone="muted">{b.room ? ROOM_LABEL[b.room] : '—'}</Pill>
                  <span className="text-ink">{b.date}</span>
                  <span className="text-muted text-xs">{b.reason}</span>
                </div>
                <button
                  className="btn-icon"
                  onClick={() => removeRoomBlock(b.id)}
                  aria-label="Remove"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="text-muted text-[11px] text-center italic pt-2">
        Every lead must move forward, close out, or be clearly parked.
      </div>
    </div>
  )
}

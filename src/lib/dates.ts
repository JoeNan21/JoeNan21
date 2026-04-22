const HOUR = 3600000
const DAY = 86400000

export function hoursSince(iso: string | null | undefined): number | null {
  if (!iso) return null
  const t = new Date(iso).getTime()
  if (Number.isNaN(t)) return null
  return (Date.now() - t) / HOUR
}

export function daysSince(iso: string | null | undefined): number | null {
  const h = hoursSince(iso)
  return h == null ? null : h / 24
}

export function isToday(iso: string | null | undefined): boolean {
  if (!iso) return false
  const d = new Date(iso)
  const n = new Date()
  return (
    d.getFullYear() === n.getFullYear() &&
    d.getMonth() === n.getMonth() &&
    d.getDate() === n.getDate()
  )
}

export function isFuture(iso: string | null | undefined): boolean {
  if (!iso) return false
  return new Date(iso).getTime() > Date.now()
}

export function gapColour(hours: number | null): 'ok' | 'warn' | 'bad' | 'muted' {
  if (hours == null) return 'muted'
  if (hours <= 24) return 'ok'
  if (hours <= 48) return 'warn'
  return 'bad'
}

export function gapLabel(hours: number | null): string {
  if (hours == null) return '—'
  if (hours < 1) return 'just now'
  if (hours < 24) return `${Math.floor(hours)}h ago`
  const d = Math.floor(hours / 24)
  return `${d}d ago`
}

export function formatNZDate(iso: string | null | undefined): string {
  if (!iso) return 'TBC'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'TBC'
  return d.toLocaleDateString('en-NZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

export function formatShortDate(iso: string | null | undefined): string {
  if (!iso) return 'TBC'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'TBC'
  return d.toLocaleDateString('en-NZ', { day: 'numeric', month: 'short' })
}

export function monthKey(iso: string): string {
  const d = new Date(iso)
  const m = String(d.getMonth() + 1).padStart(2, '0')
  return `${d.getFullYear()}-${m}`
}

export function monthLabel(key: string): string {
  const [y, m] = key.split('-').map(Number)
  const d = new Date(y, (m ?? 1) - 1, 1)
  return d.toLocaleDateString('en-NZ', { month: 'short', year: 'numeric' })
}

export function addDays(iso: string, days: number): string {
  const d = new Date(iso)
  d.setTime(d.getTime() + days * DAY)
  return d.toISOString()
}

export function todayISO(): string {
  return new Date().toISOString()
}

export function isoDateOnly(iso: string): string {
  return iso.split('T')[0]
}

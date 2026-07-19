import type { Lead } from '@/types'
import { hoursSince, isToday } from '@/lib/dates'

export function getPriorityScore(lead: Lead): number {
  const hoursSinceEnquiry = hoursSince(lead.enquiryDate) ?? 0
  const hoursSinceVisit = hoursSince(lead.visitDate)
  const hoursSinceContact = hoursSince(lead.lastContact) ?? 0

  if (lead.stage === 'new' && hoursSinceEnquiry > 24) return 100
  if (lead.stage === 'post-visit' && hoursSinceVisit != null && hoursSinceVisit <= 24) return 98
  if (lead.stage === 'post-visit' && hoursSinceVisit != null && hoursSinceVisit > 48) return 97
  if (lead.stage === 'post-visit' && hoursSinceVisit != null && hoursSinceVisit <= 48) return 95
  if (lead.stage === 'visit-booked' && isToday(lead.visitDate)) return 90
  if (lead.stage === 'contacted' && hoursSinceContact > 120) return 80
  if ((lead.estimatedValue ?? 0) > 10000 && hoursSinceContact > 72) return 70
  return 10
}

export function sortByPriority(leads: Lead[]): Lead[] {
  return [...leads].sort((a, b) => getPriorityScore(b) - getPriorityScore(a))
}

export function isOverdueNew(lead: Lead): boolean {
  return lead.stage === 'new' && (hoursSince(lead.enquiryDate) ?? 0) > 24
}

export function isOverduePostVisit(lead: Lead): boolean {
  if (lead.stage !== 'post-visit') return false
  const h = hoursSince(lead.visitDate)
  return h != null && h > 48
}

export function isStale7d(lead: Lead): boolean {
  if (lead.stage === 'lost' || lead.stage === 'confirmed') return false
  const h = hoursSince(lead.lastContact) ?? 0
  return h > 7 * 24
}

export function isTodayVisit(lead: Lead): boolean {
  return lead.stage === 'visit-booked' && isToday(lead.visitDate)
}

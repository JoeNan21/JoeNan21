import { useMemo } from 'react'
import type { Lead } from '@/types'
import {
  getPriorityScore,
  isOverdueNew,
  isOverduePostVisit,
  isStale7d,
  isTodayVisit,
  sortByPriority,
} from '@/lib/priority'

export function usePriority(leads: Lead[]) {
  return useMemo(() => {
    const active = leads.filter((l) => l.stage !== 'lost')
    const sorted = sortByPriority(active)
    const overdueNew = active.filter(isOverdueNew)
    const overduePostVisit = active.filter(isOverduePostVisit)
    const stale = active.filter(isStale7d)
    const todayVisits = active.filter(isTodayVisit)
    const scored = sorted.map((lead) => ({ lead, score: getPriorityScore(lead) }))
    return {
      sorted,
      scored,
      overdueNew,
      overduePostVisit,
      stale,
      todayVisits,
    }
  }, [leads])
}

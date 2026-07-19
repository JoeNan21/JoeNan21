import { useCallback, useEffect, useMemo, useState } from 'react'
import type { Lead, Stage } from '@/types'
import { KEYS, readJSON, writeJSON } from '@/lib/storage'
import { buildSampleLeads } from '@/lib/sampleData'
import { todayISO } from '@/lib/dates'

function applyPostVisitTrigger(lead: Lead): Lead {
  const now = new Date()
  const followUpDue = new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString()
  const stamp = now.toLocaleString('en-NZ', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
  const entry = `[${stamp}] Visit completed — 24h follow-up due`
  return {
    ...lead,
    followUpDue,
    lastContact: now.toISOString(),
    notes: lead.notes ? `${lead.notes}\n${entry}` : entry,
  }
}

function loadInitial(): Lead[] {
  const bootstrapped = localStorage.getItem(KEYS.bootstrapped)
  if (!bootstrapped) {
    const sample = buildSampleLeads()
    writeJSON(KEYS.leads, sample)
    localStorage.setItem(KEYS.bootstrapped, '1')
    return sample
  }
  return readJSON<Lead[]>(KEYS.leads, [])
}

function genId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

export function useLeads() {
  const [leads, setLeads] = useState<Lead[]>(() => loadInitial())

  useEffect(() => {
    writeJSON(KEYS.leads, leads)
  }, [leads])

  const upsert = useCallback((lead: Lead) => {
    setLeads((prev) => {
      const idx = prev.findIndex((l) => l.id === lead.id)
      if (idx === -1) return [lead, ...prev]
      const next = [...prev]
      next[idx] = lead
      return next
    })
  }, [])

  const create = useCallback((partial: Partial<Lead> & { name: string }): Lead => {
    const now = todayISO()
    const lead: Lead = {
      id: genId(),
      name: partial.name,
      eventType: partial.eventType ?? 'wedding',
      eventDate: partial.eventDate ?? null,
      guestCount: partial.guestCount ?? null,
      contactMethod: partial.contactMethod ?? 'email',
      stage: partial.stage ?? 'new',
      estimatedValue: partial.estimatedValue ?? null,
      enquiryDate: partial.enquiryDate ?? now,
      lastContact: partial.lastContact ?? now,
      visitDate: partial.visitDate ?? null,
      followUpDue: partial.followUpDue ?? null,
      depositReceived: partial.depositReceived ?? false,
      depositAmount: partial.depositAmount ?? null,
      room: partial.room ?? null,
      notes: partial.notes ?? '',
      competingVenues: partial.competingVenues ?? [],
      source: partial.source ?? '',
    }
    setLeads((prev) => [lead, ...prev])
    return lead
  }, [])

  const update = useCallback((id: string, patch: Partial<Lead>) => {
    setLeads((prev) =>
      prev.map((l) => (l.id === id ? { ...l, ...patch } : l)),
    )
  }, [])

  const setStage = useCallback((id: string, stage: Stage) => {
    setLeads((prev) =>
      prev.map((l) => {
        if (l.id !== id) return l
        const updated: Lead = { ...l, stage }
        if (stage === 'post-visit' && l.stage !== 'post-visit') {
          return applyPostVisitTrigger(updated)
        }
        return updated
      }),
    )
  }, [])

  const appendNote = useCallback((id: string, text: string) => {
    if (!text.trim()) return
    const stamp = new Date().toLocaleString('en-NZ', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
    setLeads((prev) =>
      prev.map((l) =>
        l.id === id
          ? {
              ...l,
              notes: l.notes ? `${l.notes}\n[${stamp}] ${text.trim()}` : `[${stamp}] ${text.trim()}`,
              lastContact: todayISO(),
            }
          : l,
      ),
    )
  }, [])

  const logContact = useCallback((id: string) => {
    setLeads((prev) =>
      prev.map((l) => (l.id === id ? { ...l, lastContact: todayISO() } : l)),
    )
  }, [])

  const remove = useCallback((id: string) => {
    setLeads((prev) => prev.filter((l) => l.id !== id))
  }, [])

  const byId = useCallback((id: string) => leads.find((l) => l.id === id), [leads])

  const active = useMemo(
    () => leads.filter((l) => l.stage !== 'lost'),
    [leads],
  )

  return {
    leads,
    active,
    byId,
    create,
    update,
    upsert,
    setStage,
    appendNote,
    logContact,
    remove,
  }
}

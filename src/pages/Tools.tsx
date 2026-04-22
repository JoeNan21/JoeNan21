import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Sparkles, RefreshCw, CheckCircle2, Calendar, AlarmClock } from 'lucide-react'
import { useLeadsStore, useSettingsStore } from '@/store/LeadsContext'
import { useClaude } from '@/hooks/useClaude'
import { buildCallPrepPrompt, buildCallSummaryPrompt } from '@/lib/claude'
import { Button } from '@/components/ui/Button'
import { CopyButton } from '@/components/ui/CopyButton'
import { Pill } from '@/components/ui/Pill'
import type { Lead } from '@/types'
import { EVENT_LABEL } from '@/types'
import { addDays, todayISO } from '@/lib/dates'

export function ToolsPage() {
  const { leads, update, appendNote } = useLeadsStore()
  const { settings } = useSettingsStore()
  const [params, setParams] = useSearchParams()
  const initialTab = (params.get('tab') as 'prep' | 'summary') ?? 'prep'
  const initialLeadId = params.get('leadId')
  const [tab, setTab] = useState<'prep' | 'summary'>(initialTab)
  const [leadId, setLeadId] = useState<string>(initialLeadId ?? leads[0]?.id ?? '')
  const lead = useMemo(() => leads.find((l) => l.id === leadId) ?? null, [leads, leadId])
  const [prepType, setPrepType] = useState('Wedding visit')
  const [notes, setNotes] = useState('')
  const prep = useClaude(settings.apiKey)
  const summary = useClaude(settings.apiKey)

  useEffect(() => {
    if (initialLeadId && initialLeadId !== leadId) setLeadId(initialLeadId)
  }, [initialLeadId])

  useEffect(() => {
    if (!lead) return
    switch (lead.eventType) {
      case 'wedding':
        setPrepType('Wedding visit')
        break
      case 'corporate':
        setPrepType('Corporate site inspection')
        break
      case 'funeral':
        setPrepType('Funeral/unveiling conversation')
        break
      case 'cultural':
      case 'private':
        setPrepType('Private celebration visit')
        break
    }
  }, [lead?.id, lead?.eventType])

  const updateTab = (t: 'prep' | 'summary') => {
    setTab(t)
    setParams((p) => {
      p.set('tab', t)
      return p
    })
  }

  const onLeadChange = (id: string) => {
    setLeadId(id)
    setParams((p) => {
      p.set('leadId', id)
      return p
    })
  }

  const runPrep = () => {
    if (!lead) return
    prep.generate(buildCallPrepPrompt(lead, prepType), 1500)
  }

  const runSummary = () => {
    if (!lead || !notes.trim()) return
    summary.generate(buildCallSummaryPrompt(lead, notes), 1500)
  }

  return (
    <div className="p-4 md:p-6 space-y-4 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl md:text-2xl font-semibold text-ink">Site Visit Tools</h1>
        <div className="text-muted text-xs mt-0.5">
          Prep before the visit. Process notes after.
        </div>
      </div>

      <div className="flex rounded border border-line overflow-hidden w-full md:w-auto md:inline-flex">
        <button
          onClick={() => updateTab('prep')}
          className={`flex-1 md:flex-none px-4 h-10 text-xs uppercase tracking-wider ${tab === 'prep' ? 'bg-gold text-black' : 'text-muted'}`}
        >
          Call Prep
        </button>
        <button
          onClick={() => updateTab('summary')}
          className={`flex-1 md:flex-none px-4 h-10 text-xs uppercase tracking-wider ${tab === 'summary' ? 'bg-gold text-black' : 'text-muted'}`}
        >
          Call Summary
        </button>
      </div>

      <div className="card p-4 space-y-3">
        <div>
          <label className="label">Lead</label>
          <select className="input" value={leadId} onChange={(e) => onLeadChange(e.target.value)}>
            <option value="">— Select lead —</option>
            {leads.map((l) => (
              <option key={l.id} value={l.id}>
                {l.name} — {EVENT_LABEL[l.eventType]}
              </option>
            ))}
          </select>
        </div>

        {tab === 'prep' && (
          <>
            <div>
              <label className="label">Prep Type</label>
              <select
                className="input"
                value={prepType}
                onChange={(e) => setPrepType(e.target.value)}
              >
                <option>Wedding visit</option>
                <option>Corporate site inspection</option>
                <option>Funeral/unveiling conversation</option>
                <option>Private celebration visit</option>
              </select>
            </div>
            <Button onClick={runPrep} disabled={!lead || prep.isGenerating} full>
              {prep.isGenerating ? (
                <>
                  <RefreshCw size={16} className="animate-spin" /> Generating…
                </>
              ) : (
                <>
                  <Sparkles size={16} /> {prep.output ? 'Regenerate Prep' : 'Generate Prep Brief'}
                </>
              )}
            </Button>
            {lead && lead.competingVenues.length > 0 && (
              <CompetingPanel lead={lead} />
            )}
          </>
        )}

        {tab === 'summary' && (
          <>
            <div>
              <label className="label">Raw Visit Notes</label>
              <textarea
                className="textarea"
                rows={8}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Paste or type visit notes — bullet points, transcript, or rough thoughts."
              />
            </div>
            <Button
              onClick={runSummary}
              disabled={!lead || !notes.trim() || summary.isGenerating}
              full
            >
              {summary.isGenerating ? (
                <>
                  <RefreshCw size={16} className="animate-spin" /> Processing…
                </>
              ) : (
                <>
                  <Sparkles size={16} /> {summary.output ? 'Re-process' : 'Process Notes'}
                </>
              )}
            </Button>
          </>
        )}
      </div>

      {tab === 'prep' && (prep.isGenerating || prep.output || prep.error) && (
        <OutputCard
          title="Prep Brief"
          loading={prep.isGenerating}
          error={prep.error}
          output={prep.output}
        />
      )}

      {tab === 'summary' && (summary.isGenerating || summary.output || summary.error) && (
        <>
          <OutputCard
            title="Visit Summary & Follow-Up Email"
            loading={summary.isGenerating}
            error={summary.error}
            output={summary.output}
          />
          {lead && summary.output && !summary.isGenerating && (
            <div className="card p-4 space-y-2">
              <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
                Quick Actions
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <Button
                  variant="ghost"
                  onClick={() => update(lead.id, { stage: 'post-visit' })}
                >
                  <CheckCircle2 size={14} /> Stage → Post-Visit
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => update(lead.id, { visitDate: todayISO() })}
                >
                  <Calendar size={14} /> Log Visit Today
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    update(lead.id, { followUpDue: addDays(todayISO(), 1) })
                    appendNote(lead.id, 'Follow-up scheduled for +24h')
                  }}
                >
                  <AlarmClock size={14} /> Follow-up +24h
                </Button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function OutputCard({
  title,
  loading,
  error,
  output,
}: {
  title: string
  loading: boolean
  error: string | null
  output: string
}) {
  return (
    <div className="card p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
          {title}
        </div>
        {output && !loading && <CopyButton text={output} />}
      </div>
      {loading && <div className="caos-pulse text-ink text-sm">Generating…</div>}
      {error && <div className="text-bad text-sm">{error}</div>}
      {output && !loading && (
        <pre className="whitespace-pre-wrap text-ink text-[13px] leading-relaxed font-sans">
          {output}
        </pre>
      )}
    </div>
  )
}

function CompetingPanel({ lead }: { lead: Lead }) {
  return (
    <div className="rounded border border-line bg-elevated/50 p-3">
      <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold mb-2">
        Competing Venues
      </div>
      <div className="flex flex-wrap gap-1.5">
        {lead.competingVenues.map((v) => (
          <Pill key={v} tone="teal">
            {v}
          </Pill>
        ))}
      </div>
      <div className="text-muted text-[11px] mt-2 leading-relaxed">
        Battlecard context is included automatically in the AI prep brief above.
      </div>
    </div>
  )
}

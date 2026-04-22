import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, RefreshCw, Wrench, Mail, AlertTriangle, Calendar } from 'lucide-react'
import { useLeadsStore, useSettingsStore } from '@/store/LeadsContext'
import { usePriority } from '@/hooks/usePriority'
import { useClaude } from '@/hooks/useClaude'
import { buildMorningPriorityPrompt, buildSuggestedActionsPrompt, callClaude } from '@/lib/claude'
import { Button } from '@/components/ui/Button'
import { Pill } from '@/components/ui/Pill'
import { Dot } from '@/components/ui/Dot'
import { EmptyState } from '@/components/ui/EmptyState'
import { LeadDetail } from '@/components/leads/LeadDetail'
import { EVENT_LABEL } from '@/types'
import type { Lead } from '@/types'
import { formatShortDate, gapColour, gapLabel, hoursSince } from '@/lib/dates'

export function BriefPage() {
  const navigate = useNavigate()
  const { leads } = useLeadsStore()
  const { settings } = useSettingsStore()
  const { sorted, overdueNew, overduePostVisit, stale, todayVisits } = usePriority(leads)
  const priorityAI = useClaude(settings.apiKey)
  const [suggested, setSuggested] = useState<string>('')
  const [loadingSuggested, setLoadingSuggested] = useState(false)
  const [openLead, setOpenLead] = useState<Lead | null>(null)

  const freshOpen = openLead ? leads.find((l) => l.id === openLead.id) ?? null : null

  // Stat tiles
  const stats = useMemo(() => {
    const active = leads.filter((l) => l.stage !== 'lost' && l.stage !== 'confirmed')
    const pipelineValue = active.reduce((s, l) => s + (l.estimatedValue ?? 0), 0)
    const confirmed = leads
      .filter((l) => l.stage === 'confirmed')
      .reduce((s, l) => s + (l.depositAmount ?? l.estimatedValue ?? 0), 0)
    const risk = leads.filter((l) => {
      if (l.stage === 'lost' || l.stage === 'confirmed') return false
      const h = hoursSince(l.lastContact) ?? 0
      return h > 7 * 24
    }).length
    return { active: active.length, pipelineValue, confirmed, risk }
  }, [leads])

  const refreshBrief = async () => {
    if (!settings.apiKey) {
      priorityAI.generate(buildMorningPriorityPrompt(leads)) // will set error
      return
    }
    priorityAI.generate(buildMorningPriorityPrompt(leads), 200)
    setLoadingSuggested(true)
    setSuggested('')
    try {
      const out = await callClaude({
        apiKey: settings.apiKey,
        userPrompt: buildSuggestedActionsPrompt(leads),
        maxTokens: 400,
      })
      setSuggested(out)
    } catch {
      // surfaced via priorityAI error
    } finally {
      setLoadingSuggested(false)
    }
  }

  // Overdue combined
  const overdue = [...overdueNew, ...overduePostVisit]

  return (
    <div className="p-4 md:p-6 space-y-5 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-ink">
            Morning, {settings.operatorName}.
          </h1>
          <div className="text-muted text-xs mt-0.5">
            {new Date().toLocaleDateString('en-NZ', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
            })}
          </div>
        </div>
        <Button onClick={refreshBrief} disabled={priorityAI.isGenerating || loadingSuggested}>
          <RefreshCw
            size={16}
            className={priorityAI.isGenerating || loadingSuggested ? 'animate-spin' : ''}
          />
          Refresh Brief
        </Button>
      </div>

      {/* #1 Priority */}
      <div className="card p-4 border-gold/40 bg-gold/5">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="text-gold" size={16} />
          <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
            #1 Priority Today
          </div>
        </div>
        {priorityAI.isGenerating ? (
          <div className="caos-pulse text-ink text-sm">Generating…</div>
        ) : priorityAI.error ? (
          <div className="text-bad text-sm">{priorityAI.error}</div>
        ) : priorityAI.output ? (
          <div className="text-ink text-base leading-relaxed">{priorityAI.output}</div>
        ) : (
          <div className="text-muted text-sm">
            Tap Refresh Brief to get today&rsquo;s single most important action.
          </div>
        )}
      </div>

      {/* Stat tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        <StatTile label="Active Leads" value={String(stats.active)} />
        <StatTile label="Pipeline Value" value={`$${(stats.pipelineValue / 1000).toFixed(1)}k`} />
        <StatTile
          label="Confirmed Revenue"
          value={`$${(stats.confirmed / 1000).toFixed(1)}k`}
          tone="ok"
        />
        <StatTile label="Risk (7d+ gap)" value={String(stats.risk)} tone={stats.risk > 0 ? 'bad' : 'muted'} />
      </div>

      {/* Today's visits */}
      <Section title="Today's Site Visits" icon={<Calendar size={14} />}>
        {todayVisits.length === 0 ? (
          <EmptyState title="No visits today" body="Free day to work the pipeline." />
        ) : (
          <div className="space-y-2">
            {todayVisits.map((lead) => (
              <div
                key={lead.id}
                className="card p-3 flex items-center justify-between gap-2"
              >
                <button
                  className="text-left flex-1 min-w-0"
                  onClick={() => setOpenLead(lead)}
                >
                  <div className="text-ink font-semibold text-sm">{lead.name}</div>
                  <div className="text-muted text-[11px] mt-0.5">
                    {EVENT_LABEL[lead.eventType]}
                    {lead.guestCount ? ` · ${lead.guestCount} pax` : ''}
                  </div>
                </button>
                <Button
                  variant="teal"
                  onClick={() => navigate(`/tools?leadId=${lead.id}&tab=prep`)}
                >
                  <Wrench size={14} /> Prep Me
                </Button>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Overdue */}
      <Section title="Overdue Follow-Ups" icon={<AlertTriangle size={14} />}>
        {overdue.length === 0 ? (
          <EmptyState title="Nothing overdue" body="Response times look clean." />
        ) : (
          <div className="space-y-2">
            {overdue.map((lead) => {
              const reason = overdueNew.includes(lead)
                ? 'Enquiry unreplied'
                : 'Post-visit follow-up due'
              const gap = hoursSince(lead.lastContact)
              return (
                <div
                  key={lead.id}
                  className="card p-3 flex items-center justify-between gap-2"
                >
                  <button
                    className="text-left flex-1 min-w-0"
                    onClick={() => setOpenLead(lead)}
                  >
                    <div className="flex items-center gap-2">
                      <Dot tone={gapColour(gap)} />
                      <div className="text-ink font-semibold text-sm truncate">{lead.name}</div>
                    </div>
                    <div className="text-muted text-[11px] mt-0.5">
                      {reason} · {gapLabel(gap)}
                    </div>
                  </button>
                  <Button
                    variant="gold"
                    onClick={() => navigate(`/composer?leadId=${lead.id}`)}
                  >
                    <Mail size={14} /> Draft
                  </Button>
                </div>
              )
            })}
          </div>
        )}
      </Section>

      {/* Suggested Actions */}
      <Section title="Suggested Actions" icon={<Sparkles size={14} />}>
        {loadingSuggested ? (
          <div className="caos-pulse text-ink text-sm p-3">Generating…</div>
        ) : suggested ? (
          <div className="space-y-1.5">
            {suggested
              .split('\n')
              .map((s) => s.trim())
              .filter(Boolean)
              .map((line, i) => {
                const match = leads.find((l) => line.toLowerCase().includes(l.name.toLowerCase()))
                return (
                  <button
                    key={i}
                    onClick={() => match && setOpenLead(match)}
                    className="card p-3 w-full text-left text-sm text-ink hover:border-gold/50 transition-colors"
                  >
                    {line}
                  </button>
                )
              })}
          </div>
        ) : (
          <EmptyState
            title="Get 3 priority actions"
            body="AI will scan the pipeline and return the 3 best moves for today."
            action={
              <Button onClick={refreshBrief}>
                <Sparkles size={14} /> Generate Actions
              </Button>
            }
          />
        )}
      </Section>

      {/* Priority list (no AI) */}
      <Section title="Priority Queue">
        <div className="space-y-2">
          {sorted.slice(0, 6).map((lead) => (
            <button
              key={lead.id}
              className="card p-3 w-full text-left hover:border-gold/50 transition-colors"
              onClick={() => setOpenLead(lead)}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="min-w-0">
                  <div className="text-ink text-sm font-semibold truncate">{lead.name}</div>
                  <div className="text-muted text-[11px] mt-0.5">
                    {EVENT_LABEL[lead.eventType]} · {formatShortDate(lead.eventDate)}
                  </div>
                </div>
                <Pill tone={gapColour(hoursSince(lead.lastContact)) === 'bad' ? 'bad' : 'muted'}>
                  {gapLabel(hoursSince(lead.lastContact))}
                </Pill>
              </div>
            </button>
          ))}
          {sorted.length === 0 && (
            <EmptyState
              title="No active leads"
              body="Add your first lead to start the queue."
              action={
                <Button onClick={() => navigate('/pipeline')}>Open Pipeline</Button>
              }
            />
          )}
        </div>
      </Section>

      {/* Stale */}
      {stale.length > 0 && (
        <Section title="Gone Quiet (7d+)">
          <div className="space-y-2">
            {stale.map((lead) => (
              <button
                key={lead.id}
                className="card p-3 w-full text-left hover:border-gold/50 transition-colors flex items-center justify-between"
                onClick={() => setOpenLead(lead)}
              >
                <div>
                  <div className="text-ink text-sm font-semibold">{lead.name}</div>
                  <div className="text-bad text-[11px] mt-0.5">{gapLabel(hoursSince(lead.lastContact))}</div>
                </div>
                <Mail size={14} className="text-muted" />
              </button>
            ))}
          </div>
        </Section>
      )}

      <LeadDetail lead={freshOpen} open={!!openLead} onClose={() => setOpenLead(null)} />
    </div>
  )
}

function StatTile({
  label,
  value,
  tone = 'muted',
}: {
  label: string
  value: string
  tone?: 'muted' | 'ok' | 'bad'
}) {
  return (
    <div className="card p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted mb-1">{label}</div>
      <div
        className={`text-xl font-semibold ${
          tone === 'ok' ? 'text-ok' : tone === 'bad' ? 'text-bad' : 'text-ink'
        }`}
      >
        {value}
      </div>
    </div>
  )
}

function Section({
  title,
  icon,
  children,
}: {
  title: string
  icon?: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2 px-0.5">
        {icon && <span className="text-gold">{icon}</span>}
        <h2 className="text-[11px] uppercase tracking-[0.2em] text-muted font-semibold">
          {title}
        </h2>
      </div>
      {children}
    </div>
  )
}

import { useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Sparkles, RefreshCw } from 'lucide-react'
import { useLeadsStore, useSettingsStore } from '@/store/LeadsContext'
import { useClaude } from '@/hooks/useClaude'
import {
  buildForecastSummaryPrompt,
  buildPipelineReviewPrompt,
} from '@/lib/claude'
import { Button } from '@/components/ui/Button'
import { CopyButton } from '@/components/ui/CopyButton'
import { Pill } from '@/components/ui/Pill'
import { STAGE_WEIGHT } from '@/types'
import { monthKey, monthLabel } from '@/lib/dates'

function nextMonths(n: number): string[] {
  const out: string[] = []
  const d = new Date()
  d.setDate(1)
  for (let i = 0; i < n; i++) {
    out.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`)
    d.setMonth(d.getMonth() + 1)
  }
  return out
}

export function ForecastPage() {
  const { leads } = useLeadsStore()
  const { settings } = useSettingsStore()
  const [tab, setTab] = useState<'review' | 'forecast'>('review')
  const review = useClaude(settings.apiKey)
  const summary = useClaude(settings.apiKey)

  const months = useMemo(() => nextMonths(6), [])

  const data = useMemo(() => {
    return months.map((key) => {
      const target = settings.monthlyTargets[key] ?? 0
      let confirmed = 0
      let weighted = 0
      for (const l of leads) {
        if (!l.eventDate) continue
        const k = monthKey(l.eventDate)
        if (k !== key) continue
        if (l.stage === 'lost') continue
        if (l.stage === 'confirmed') {
          confirmed += l.depositAmount ?? l.estimatedValue ?? 0
        } else {
          weighted += (l.estimatedValue ?? 0) * STAGE_WEIGHT[l.stage]
        }
      }
      return {
        key,
        label: monthLabel(key),
        confirmed: Math.round(confirmed),
        weighted: Math.round(weighted),
        target,
      }
    })
  }, [leads, months, settings.monthlyTargets])

  const maxTarget = Math.max(...data.map((d) => d.target), 0)

  const generateReview = () => {
    review.generate(buildPipelineReviewPrompt(leads), 1200)
  }

  const generateSummary = () => {
    const first = data.find((d) => d.target > 0) ?? data[0]
    summary.generate(
      buildForecastSummaryPrompt(leads, {
        month: first.label,
        target: first.target,
        confirmed: first.confirmed,
        weighted: first.weighted,
      }),
      400,
    )
  }

  return (
    <div className="p-4 md:p-6 space-y-4 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl md:text-2xl font-semibold text-ink">Forecast & Review</h1>
        <div className="text-muted text-xs mt-0.5">Weekly pipeline review and 6-month outlook.</div>
      </div>

      <div className="flex rounded border border-line overflow-hidden w-full md:w-auto md:inline-flex">
        <button
          onClick={() => setTab('review')}
          className={`flex-1 md:flex-none px-4 h-10 text-xs uppercase tracking-wider ${
            tab === 'review' ? 'bg-gold text-black' : 'text-muted'
          }`}
        >
          Pipeline Review
        </button>
        <button
          onClick={() => setTab('forecast')}
          className={`flex-1 md:flex-none px-4 h-10 text-xs uppercase tracking-wider ${
            tab === 'forecast' ? 'bg-gold text-black' : 'text-muted'
          }`}
        >
          Forecast
        </button>
      </div>

      {tab === 'review' && (
        <div className="space-y-4">
          <div className="card p-4">
            <div className="flex items-center justify-between gap-2 mb-3">
              <div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
                  Weekly Review
                </div>
                <div className="text-muted text-xs mt-0.5">
                  Health score, risk flags, three actions for the week.
                </div>
              </div>
              <Button onClick={generateReview} disabled={review.isGenerating}>
                {review.isGenerating ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" /> Generating…
                  </>
                ) : (
                  <>
                    <Sparkles size={16} /> {review.output ? 'Regenerate' : 'Generate Review'}
                  </>
                )}
              </Button>
            </div>
            {review.error && <div className="text-bad text-sm">{review.error}</div>}
            {review.isGenerating && (
              <div className="caos-pulse text-ink text-sm">Generating…</div>
            )}
            {review.output && !review.isGenerating && (
              <div>
                <div className="flex justify-end mb-2">
                  <CopyButton text={review.output} />
                </div>
                <pre className="whitespace-pre-wrap text-ink text-[13px] leading-relaxed font-sans">
                  {review.output}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === 'forecast' && (
        <div className="space-y-4">
          <div className="card p-4">
            <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold mb-3">
              6-Month Outlook
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke="#2a2a2a" strokeDasharray="3 3" />
                  <XAxis
                    dataKey="label"
                    tick={{ fill: '#9a9590', fontSize: 11 }}
                    axisLine={{ stroke: '#2a2a2a' }}
                  />
                  <YAxis
                    tick={{ fill: '#9a9590', fontSize: 11 }}
                    axisLine={{ stroke: '#2a2a2a' }}
                    tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#111111',
                      border: '1px solid #2a2a2a',
                      borderRadius: 6,
                      color: '#f0ede8',
                      fontSize: 12,
                    }}
                    formatter={(v: number) => `$${v.toLocaleString()}`}
                  />
                  <Bar dataKey="confirmed" stackId="a" name="Confirmed" fill="#c9a84c" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="weighted" stackId="a" name="Weighted Pipeline" fill="#2a6b6b" radius={[4, 4, 0, 0]} />
                  {maxTarget > 0 && (
                    <ReferenceLine
                      y={maxTarget}
                      stroke="#9a9590"
                      strokeDasharray="4 4"
                      label={{ value: 'Target', fill: '#9a9590', fontSize: 10, position: 'right' }}
                    />
                  )}
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3">
              {data.map((d) => {
                const total = d.confirmed + d.weighted
                const gap = d.target - total
                return (
                  <div key={d.key} className="rounded border border-line p-2.5">
                    <div className="text-[11px] uppercase tracking-wider text-muted">
                      {d.label}
                    </div>
                    <div className="text-ink text-sm font-semibold mt-1">
                      ${(total / 1000).toFixed(1)}k
                    </div>
                    {d.target > 0 && (
                      <div className="text-[11px] mt-0.5">
                        <Pill tone={gap <= 0 ? 'ok' : gap < d.target * 0.25 ? 'warn' : 'bad'}>
                          {gap <= 0 ? 'On target' : `Gap $${(gap / 1000).toFixed(1)}k`}
                        </Pill>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          <div className="card p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[10px] uppercase tracking-[0.2em] text-gold font-semibold">
                Forecast Summary
              </div>
              <Button onClick={generateSummary} disabled={summary.isGenerating}>
                {summary.isGenerating ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" /> Generating…
                  </>
                ) : (
                  <>
                    <Sparkles size={16} /> {summary.output ? 'Regenerate' : 'Generate Summary'}
                  </>
                )}
              </Button>
            </div>
            {summary.error && <div className="text-bad text-sm">{summary.error}</div>}
            {summary.isGenerating && (
              <div className="caos-pulse text-ink text-sm">Generating…</div>
            )}
            {summary.output && !summary.isGenerating && (
              <div>
                <div className="flex justify-end mb-2">
                  <CopyButton text={summary.output} />
                </div>
                <pre className="whitespace-pre-wrap text-ink text-[14px] leading-relaxed font-sans">
                  {summary.output}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

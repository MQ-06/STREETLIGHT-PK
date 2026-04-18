// Module 3 — fetches /insights and renders 3 AI insight cards
import { useState, useEffect } from 'react'
import { authFetch } from '../../utils/auth'
import AIInsightCard, { AIInsightCardSkeleton } from './AIInsightCard'

export default function InsightRow({ scope, scopeId, days, compact = false }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setData(null)

    const params = new URLSearchParams({ scope, scope_id: scopeId || '', days })
    authFetch(`/admin/analytics/insights?${params}`)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [scope, scopeId, days])

  if (loading) {
    return (
      <div className={compact ? 'flex flex-col gap-3' : 'grid grid-cols-3 gap-4'}>
        {[0, 1, 2].map(i => <AIInsightCardSkeleton key={i} />)}
      </div>
    )
  }

  if (!data) return null

  const { forecast, bottleneck, health } = data

  // ── Forecast card ──────────────────────────────────────────────────────────
  const fDelta = forecast.delta
  const fValue = fDelta === 0 ? '~0' : `${fDelta > 0 ? '+' : ''}${fDelta}`
  const fSub   = forecast.direction === 'up'
    ? 'Reports trending up vs prior period'
    : forecast.direction === 'down'
    ? 'Reports trending down — improving'
    : 'Volume steady vs prior period'

  // ── Bottleneck card ────────────────────────────────────────────────────────
  const bnValue = bottleneck.label ?? 'None'
  const bnSub   = bottleneck.count > 0
    ? `${bottleneck.count} reports · ${bottleneck.pct}% of pipeline`
    : 'No active bottleneck'

  // ── Health card ────────────────────────────────────────────────────────────
  const hValue = health.index != null ? `${health.index}` : '—'
  const hSub   = health.label   // "Healthy" | "At Risk" | "Critical"

  return (
    <div className={compact ? 'flex flex-col gap-3' : 'grid grid-cols-3 gap-4'}>
      <AIInsightCard
        type="forecast"
        value={fValue}
        label="30-Day Forecast"
        sub={fSub}
        direction={forecast.direction}
      />
      <AIInsightCard
        type="bottleneck"
        value={bnValue}
        label="Current Bottleneck"
        sub={bnSub}
      />
      <AIInsightCard
        type={health.label === 'Critical' ? 'critical' : 'health'}
        value={hValue}
        label="Citizen Health Index"
        sub={hSub}
      />
    </div>
  )
}

import { useState, useEffect } from 'react'
import KpiCard, { KpiCardSkeleton } from './KpiCard'
import { authFetchJson } from '../../utils/auth'

function signalToColor(signal) {
  return signal === 'red' ? 'red' : signal === 'amber' ? 'amber' : 'green'
}

export default function KpiRow({ scope, scopeId, days = 30 }) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setData(null)

    const params = new URLSearchParams({ scope, scope_id: scopeId || '', days })
    authFetchJson(`/admin/analytics/kpi?${params}`)
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [scope, scopeId, days])

  if (loading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
        {[0, 1, 2, 3].map(i => <KpiCardSkeleton key={i} />)}
      </div>
    )
  }

  if (!data) return null

  const { total_reports, avg_resolution_time, re_report_rate, community_score } = data

  const cards = [
    {
      label: 'Total Reports (30d)',
      value: String(total_reports.value),
      delta: {
        text:  `${total_reports.delta_pct >= 0 ? '+' : ''}${total_reports.delta_pct}%`,
        color: signalToColor(total_reports.signal),
      },
      icon: total_reports.signal === 'red' ? 'warn' : null,
    },
    {
      label: 'Avg Resolution Time',
      value: `${avg_resolution_time.value_days}d`,
      delta: {
        text:  `${avg_resolution_time.delta_days >= 0 ? '+' : ''}${avg_resolution_time.delta_days}d`,
        color: signalToColor(avg_resolution_time.signal),
      },
      icon: avg_resolution_time.signal === 'red' ? 'warn' : null,
    },
    {
      label: 'Re-report Rate',
      value: `${re_report_rate.value_pct}%`,
      delta: {
        text:  `${re_report_rate.delta_pp >= 0 ? '+' : ''}${re_report_rate.delta_pp}pp`,
        color: signalToColor(re_report_rate.signal),
      },
      icon: re_report_rate.signal === 'red' ? 'warn' : null,
    },
    {
      label: 'Community Score',
      value: community_score.value != null ? String(community_score.value) : 'N/A',
      delta: community_score.delta != null ? {
        text:  `${community_score.delta >= 0 ? '+' : ''}${community_score.delta}`,
        color: signalToColor(community_score.signal),
      } : null,
      icon: community_score.signal === 'green' ? 'check'
          : community_score.signal === 'red'   ? 'warn'
          : null,
    },
  ]

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
      {cards.map(c => <KpiCard key={c.label} {...c} />)}
    </div>
  )
}

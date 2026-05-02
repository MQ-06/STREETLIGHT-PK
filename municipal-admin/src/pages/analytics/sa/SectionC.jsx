// SA Module 4 — Section C: City-Wide Charts (3-column layout)
// Left: Donut | Middle: Pipeline avg-days bars | Right: 3 AI mini-cards
import { useState, useEffect } from 'react'
import { authFetchJson } from '../../../utils/auth'
import DonutChart from '../../../components/analytics/DonutChart'

// ── Colour palette (matches spec) ─────────────────────────────────────────────
const DONUT_COLORS = {
  POTHOLE: '#E8612D',
  TRASH:   '#22C55E',
  UNKNOWN: '#64748B',
}
const DEFAULT_COLOR = '#3B82F6'

// Pipeline stage display names (shortened for the bar chart)
const STAGE_SHORT = {
  NEW:                  'Reported',
  PENDING_VERIFICATION: 'Under Review',
  VERIFIED:             'Verified',
  IN_PROGRESS:          'In Progress',
  AWAITING_FEEDBACK:    'Dispatched',
  RESOLVED:             'Resolved',
  CLOSED:               'Closed',
}

// Bar colours — gradient-ish orange → amber → green for resolved
const BAR_COLOR = {
  NEW:                  '#E8612D',
  PENDING_VERIFICATION: '#F97316',
  VERIFIED:             '#F59E0B',
  IN_PROGRESS:          '#EAB308',
  AWAITING_FEEDBACK:    '#84CC16',
  RESOLVED:             '#22C55E',
  CLOSED:               '#15803D',
}

// ── Skeletons ─────────────────────────────────────────────────────────────────
function PanelSkeleton({ height = 280 }) {
  return (
    <div
      className="bg-white rounded-2xl border border-warm-border animate-pulse"
      style={{ height }}
    />
  )
}

// ── Left panel — Donut Chart ─────────────────────────────────────────────────
function DonutPanel({ days }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    authFetchJson(`/admin/analytics/issue-breakdown?scope=national&scope_id=&days=${days}`)
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [days])

  if (loading) return <PanelSkeleton />

  // Map to DonutChart expected shape, inject spec colors
  const chartData = (data?.breakdown ?? []).map(item => ({
    ...item,
    color: DONUT_COLORS[item.category] ?? DEFAULT_COLOR,
  }))

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
        Issue Type Breakdown <span className="text-gray-300">· city total</span>
      </p>

      {/* Donut + legend */}
      <div style={{ height: 200 }}>
        <DonutChart data={chartData} />
      </div>

      {/* Custom coloured legend */}
      <div className="flex flex-col gap-1.5 mt-1">
        {chartData.map(item => (
          <div key={item.category} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ background: item.color }}
              />
              <span className="text-xs text-gray-600">
                {item.category.charAt(0) + item.category.slice(1).toLowerCase()}
              </span>
            </div>
            <span className="text-xs font-semibold text-gray-700">{item.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Middle panel — Pipeline avg-days horizontal bars ─────────────────────────
function PipelinePanel({ days }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    authFetchJson(`/admin/analytics/pipeline?scope=national&scope_id=&days=${days}`)
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [days])

  if (loading) return <PanelSkeleton />

  const stages  = data?.stages ?? []
  const maxDays = Math.max(...stages.map(s => s.avg_days), 1)

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-4">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
        Pipeline Lifecycle <span className="text-gray-300">· city avg days</span>
      </p>

      <div className="flex flex-col gap-3">
        {stages.map(s => {
          const widthPct = maxDays > 0 ? (s.avg_days / maxDays) * 100 : 0
          const color    = BAR_COLOR[s.stage] ?? '#94A3B8'
          const label    = STAGE_SHORT[s.stage] ?? s.label

          return (
            <div key={s.stage} className="flex flex-col gap-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600 font-medium">{label}</span>
                <span className="font-bold text-gray-800">
                  {s.avg_days > 0 ? `${s.avg_days}d` : '—'}
                </span>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${widthPct}%`, background: color }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── Right panel — 3 AI mini-cards ─────────────────────────────────────────────
function AiPanel({ days }) {
  const [insights,  setInsights]  = useState(null)
  const [cityData,  setCityData]  = useState(null)
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    Promise.allSettled([
      authFetchJson(`/admin/analytics/insights?scope=national&scope_id=&days=${days}`),
      authFetchJson(`/admin/analytics/city-overview?days=${days}`),
    ])
      .then(([insResult, cityResult]) => {
        if (!cancelled) {
          setInsights(insResult.status === 'fulfilled' ? insResult.value : null)
          setCityData(cityResult.status === 'fulfilled' ? cityResult.value : null)
          setLoading(false)
        }
      })

    return () => { cancelled = true }
  }, [days])

  if (loading) {
    return (
      <div className="flex flex-col gap-3">
        {[0,1,2].map(i => <PanelSkeleton key={i} height={88} />)}
      </div>
    )
  }

  // Worst city by risk then avg_res_days
  const cities    = cityData?.cities ?? []
  const worstCity = cities.length > 0
    ? [...cities].sort((a, b) => {
        const riskRank = { HIGH: 0, MED: 1, LOW: 2 }
        if (riskRank[a.risk] !== riskRank[b.risk]) return riskRank[a.risk] - riskRank[b.risk]
        return b.avg_res_days - a.avg_res_days
      })[0]
    : null

  const forecast  = insights?.forecast  ?? {}
  const health    = insights?.health    ?? {}

  const fDelta    = forecast.delta ?? 0
  const fSign     = fDelta > 0 ? '+' : ''
  const fColor    = fDelta > 0 ? '#DC2626' : fDelta < 0 ? '#15803D' : '#6B7280'
  const fSub      = forecast.direction === 'up'   ? 'Rising trend'
                  : forecast.direction === 'down'  ? 'Improving trend'
                  : 'Stable volume'

  const healthColor = health.label === 'Healthy' ? '#15803D'
                    : health.label === 'At Risk'  ? '#B45309'
                    : '#DC2626'

  const bnCity  = worstCity?.label ?? '—'
  const bnDays  = worstCity?.avg_res_days ?? '—'
  const bnNote  = worstCity ? `${worstCity.bottleneck ?? 'N/A'}` : '—'

  return (
    <div className="flex flex-col gap-3">

      {/* Card 1 — City Forecast */}
      <div className="bg-white rounded-2xl border border-warm-border p-4 flex flex-col gap-1"
           style={{ borderLeft: '4px solid #E8612D' }}>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">City Forecast (30d)</p>
        <p className="text-2xl font-black leading-none" style={{ color: fColor }}>
          {fSign}{fDelta}
        </p>
        <p className="text-xs" style={{ color: fColor }}>{fSub}</p>
      </div>

      {/* Card 2 — Worst Bottleneck */}
      <div className="bg-white rounded-2xl border border-warm-border p-4 flex flex-col gap-1"
           style={{ borderLeft: '4px solid #F59E0B' }}>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">Worst Bottleneck</p>
        <p className="text-xl font-black text-gray-900 leading-none">
          {bnCity} <span className="text-amber-500">{bnDays}d</span>
        </p>
        <p className="text-xs text-gray-400">{bnNote}</p>
      </div>

      {/* Card 3 — City Health Index */}
      <div className="bg-white rounded-2xl border border-warm-border p-4 flex flex-col gap-1"
           style={{ borderLeft: '4px solid #22C55E' }}>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">City Health Index</p>
        <p className="text-2xl font-black leading-none" style={{ color: healthColor }}>
          {health.index ?? '—'}<span className="text-sm font-semibold text-gray-400">/100</span>
        </p>
        <p className="text-xs text-gray-400">
          {health.label}
          {worstCity && <span className="text-red-400 ml-1">· {worstCity.label} low</span>}
        </p>
      </div>

    </div>
  )
}

// ── Section C ─────────────────────────────────────────────────────────────────
export default function SectionC({ days }) {
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
        City-Wide Charts &nbsp;·&nbsp; aggregated across all municipal areas
      </p>
      <div className="grid grid-cols-3 gap-4">
        <DonutPanel   days={days} />
        <PipelinePanel days={days} />
        <AiPanel      days={days} />
      </div>
    </div>
  )
}

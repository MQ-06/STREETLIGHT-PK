// SA Module 2 — Section A: City-Wide KPI Strip (warm beige design system)
import { useState, useEffect } from 'react'
import { authFetch } from '../../../utils/auth'

// ── Pill ─────────────────────────────────────────────────────────────────────
const PILL = {
  good:    { bg: '#F0FDF4', text: '#15803D' },
  warn:    { bg: '#FFFBEB', text: '#B45309' },
  bad:     { bg: '#FEF2F2', text: '#DC2626' },
  neutral: { bg: '#F1F5F9', text: '#64748B' },
}

function Pill({ label, signal }) {
  const c = PILL[signal] ?? PILL.neutral
  return (
    <span
      className="text-xs font-bold px-2 py-0.5 rounded-full whitespace-nowrap"
      style={{ backgroundColor: c.bg, color: c.text }}
    >
      {label}
    </span>
  )
}

// ── Single KPI card ───────────────────────────────────────────────────────────
function KpiCard({ label, value, sub, pillLabel, signal }) {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-2">
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="text-3xl font-black text-gray-900 leading-none">{value ?? '—'}</p>
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <p className="text-xs text-gray-400">{sub}</p>
        {pillLabel && <Pill label={pillLabel} signal={signal} />}
      </div>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
function KpiSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3 animate-pulse">
      <div className="h-3 w-24 bg-gray-100 rounded" />
      <div className="h-8 w-20 bg-gray-100 rounded" />
      <div className="h-4 w-16 bg-gray-100 rounded-full" />
    </div>
  )
}

// ── Section A ─────────────────────────────────────────────────────────────────
export default function SectionA({ days }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setData(null)

    authFetch(`/admin/analytics/kpi?scope=national&scope_id=&days=${days}`)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [days])

  function buildCards(d) {
    const tr  = d.total_reports
    const res = d.avg_resolution_time
    const rr  = d.re_report_rate
    const cs  = d.community_score

    return [
      {
        label:     'Total Reports (30d)',
        value:     tr.value?.toLocaleString() ?? '—',
        sub:       'across all areas',
        pillLabel: tr.delta_pct >= 0 ? `+${tr.delta_pct}%` : `${tr.delta_pct}%`,
        signal:    tr.signal ?? 'neutral',
      },
      {
        label:     'Avg Resolution Time',
        value:     `${res.value_days}d`,
        sub:       'city average',
        pillLabel: res.delta_days >= 0 ? `+${res.delta_days}d` : `${res.delta_days}d`,
        signal:    res.signal,
      },
      {
        label:     'Re-report Rate',
        value:     `${rr.value_pct}%`,
        sub:       'city-wide signal',
        pillLabel: rr.value_pct > 25 ? 'Above 25%' : rr.delta_pp >= 0 ? `+${rr.delta_pp}pp` : `${rr.delta_pp}pp`,
        signal:    rr.signal,
      },
      {
        label:     'Community Score',
        value:     cs.value ?? '—',
        sub:       'city avg health',
        pillLabel: cs.delta != null ? (cs.delta >= 0 ? `+${cs.delta} pts` : `${cs.delta} pts`) : null,
        signal:    cs.signal ?? 'neutral',
      },
    ]
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Section subtitle */}
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
        City-Wide Aggregate &nbsp;·&nbsp; all municipal areas combined
      </p>

      {/* 4-col KPI grid */}
      <div className="grid grid-cols-4 gap-4">
        {loading
          ? [0, 1, 2, 3].map(i => <KpiSkeleton key={i} />)
          : data
            ? buildCards(data).map(c => <KpiCard key={c.label} {...c} />)
            : <p className="text-sm text-gray-400 col-span-4">Failed to load KPIs.</p>
        }
      </div>
    </div>
  )
}

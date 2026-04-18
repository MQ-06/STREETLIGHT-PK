// SA Module 2 — Section A: City-Wide KPI Strip
import { useState, useEffect } from 'react'
import { authFetch } from '../../../utils/auth'
import { SA } from '../sa-theme'

// ── Pill ─────────────────────────────────────────────────────────────────────
function Pill({ label, signal }) {
  const colors = {
    good:    { bg: 'rgba(34,197,94,0.15)',  text: '#22C55E' },
    warn:    { bg: 'rgba(245,158,11,0.15)', text: '#F59E0B' },
    bad:     { bg: 'rgba(239,68,68,0.15)',  text: '#EF4444' },
    neutral: { bg: 'rgba(100,116,139,0.15)', text: '#64748B' },
  }
  const c = colors[signal] ?? colors.neutral
  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: 6,
        fontSize: 11,
        fontWeight: 700,
        background: c.bg,
        color: c.text,
        letterSpacing: '0.2px',
      }}
    >
      {label}
    </span>
  )
}

// ── Single KPI card ───────────────────────────────────────────────────────────
function KpiCard({ label, value, sub, pillLabel, signal }) {
  return (
    <div style={{ ...SA.cardStyle, padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 10 }}>
      <p style={{ margin: 0, fontSize: 11, fontWeight: 600, color: SA.muted, textTransform: 'uppercase', letterSpacing: '0.6px' }}>
        {label}
      </p>
      <p style={{ margin: 0, fontSize: 28, fontWeight: 800, color: SA.text, lineHeight: 1 }}>
        {value ?? '—'}
      </p>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <p style={{ margin: 0, fontSize: 12, color: SA.muted }}>{sub}</p>
        {pillLabel && <Pill label={pillLabel} signal={signal} />}
      </div>
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
function KpiSkeleton() {
  return (
    <div
      style={{
        ...SA.cardStyle,
        padding: '20px 22px',
        height: 108,
        background: 'rgba(17,26,46,0.6)',
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
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

  // ── Derive display values from API response ──────────────────────────────
  function buildCards(d) {
    const tr    = d.total_reports
    const res   = d.avg_resolution_time
    const rr    = d.re_report_rate
    const cs    = d.community_score

    const trPct   = tr.delta_pct
    const resDays = res.delta_days

    return [
      {
        label:     'Total Reports (30d)',
        value:     tr.value.toLocaleString(),
        sub:       'across all areas',
        pillLabel: trPct >= 0 ? `+${trPct}%` : `${trPct}%`,
        signal:    tr.signal,
      },
      {
        label:     'Avg Resolution Time',
        value:     `${res.value_days}d`,
        sub:       'city average',
        pillLabel: resDays >= 0 ? `+${resDays}d` : `${resDays}d`,
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
        signal:    cs.signal,
      },
    ]
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Section label */}
      <p style={{ margin: 0, fontSize: 11, fontWeight: 600, color: SA.muted, textTransform: 'uppercase', letterSpacing: '1px' }}>
        City-Wide Aggregate &nbsp;·&nbsp; all municipal areas combined
      </p>

      {/* 4-col KPI grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        {loading
          ? [0, 1, 2, 3].map(i => <KpiSkeleton key={i} />)
          : data
            ? buildCards(data).map(c => <KpiCard key={c.label} {...c} />)
            : <p style={{ color: SA.muted, fontSize: 13 }}>Failed to load</p>
        }
      </div>
    </div>
  )
}

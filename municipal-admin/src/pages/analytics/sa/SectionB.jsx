// SA Module 3 — Section B: Municipal Area Breakdown Cards (warm beige theme)
import { useState, useEffect } from 'react'
import { authFetch } from '../../../utils/auth'

// ── Risk badge config ─────────────────────────────────────────────────────────
const RISK = {
  HIGH: { bg: '#FEE2E2', text: '#DC2626', label: 'HIGH RISK' },
  MED:  { bg: '#FEF3C7', text: '#B45309', label: 'MED RISK'  },
  LOW:  { bg: '#DCFCE7', text: '#15803D', label: 'LOW RISK'  },
}

// ── Colour helpers ────────────────────────────────────────────────────────────
function resColor(days) {
  if (days > 7)  return '#DC2626'
  if (days > 4)  return '#B45309'
  return '#15803D'
}
function reColor(pct) {
  if (pct > 25)  return '#DC2626'
  if (pct > 15)  return '#B45309'
  return '#15803D'
}
function civicColor(score) {
  if (score == null) return '#9CA3AF'
  if (score < 60)    return '#DC2626'
  if (score < 80)    return '#B45309'
  return '#15803D'
}

// Forecast pill: >20 red, 1-20 amber, <=0 green
function forecastPill(delta) {
  const sign  = delta > 0 ? '+' : ''
  const label = `30d forecast: ${sign}${delta} reports`
  if (delta > 20)  return { label, bg: '#FEE2E2', text: '#DC2626' }
  if (delta > 0)   return { label, bg: '#FEF3C7', text: '#B45309' }
  return             { label, bg: '#DCFCE7', text: '#15803D' }
}

// ── Metric cell ───────────────────────────────────────────────────────────────
function MetricCell({ label, value, color }) {
  return (
    <div className="flex flex-col gap-0.5">
      <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
      <p className="text-sm font-bold" style={{ color: color || '#111827' }}>
        {value ?? '—'}
      </p>
    </div>
  )
}

// ── Single city card ──────────────────────────────────────────────────────────
function CityCard({ city }) {
  const risk = RISK[city.risk] ?? RISK.LOW
  const fp   = forecastPill(city.forecast_delta ?? 0)

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3">

      {/* 1. Zone name + risk badge */}
      <div className="flex items-start justify-between gap-2">
        <p className="text-base font-black text-gray-900 leading-tight">{city.label}</p>
        <span
          className="shrink-0 text-xs font-bold px-2 py-0.5 rounded-md"
          style={{ backgroundColor: risk.bg, color: risk.text }}
        >
          {risk.label}
        </span>
      </div>

      {/* 2. Admin name */}
      {city.admin_name && (
        <p className="text-xs text-gray-400 -mt-2">Admin: {city.admin_name}</p>
      )}

      {/* 3. Divider */}
      <hr className="border-warm-border" />

      {/* 4. 2×2 metric grid */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-2">
        <MetricCell label="Reports"    value={city.total} />
        <MetricCell label="Avg Res."   value={`${city.avg_res_days}d`}  color={resColor(city.avg_res_days)} />
        <MetricCell label="Re-report"  value={`${city.re_rate}%`}       color={reColor(city.re_rate)} />
        <MetricCell label="Civic Score" value={city.civic_score}        color={civicColor(city.civic_score)} />
      </div>

      {/* 5. Top issue */}
      {city.top_category && (
        <p className="text-xs text-gray-500">
          Top Issue:{' '}
          <span className="font-semibold text-gray-700">
            {city.top_category} ({city.top_cat_pct}%)
          </span>
        </p>
      )}

      {/* 6. Bottleneck */}
      {city.bottleneck ? (
        <p className="text-xs font-medium text-amber-600">
          {city.bottleneck}{city.bn_avg_days != null ? ` · ${city.bn_avg_days}d` : ''}
        </p>
      ) : (
        <p className="text-xs font-medium text-green-600">No bottleneck</p>
      )}

      {/* 7. Forecast pill */}
      <span
        className="self-start text-xs font-bold px-2.5 py-1 rounded-full mt-auto"
        style={{ backgroundColor: fp.bg, color: fp.text }}
      >
        {fp.label}
      </span>

    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
function CardSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3 animate-pulse h-72">
      <div className="h-4 w-32 bg-gray-100 rounded" />
      <div className="h-3 w-20 bg-gray-100 rounded" />
      <hr className="border-warm-border" />
      <div className="grid grid-cols-2 gap-3">
        {[0,1,2,3].map(i => <div key={i} className="h-8 bg-gray-100 rounded" />)}
      </div>
      <div className="h-3 w-28 bg-gray-100 rounded" />
      <div className="h-3 w-24 bg-gray-100 rounded" />
      <div className="h-6 w-36 bg-gray-100 rounded-full mt-auto" />
    </div>
  )
}

// ── Section B ─────────────────────────────────────────────────────────────────
export default function SectionB({ days }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setData(null)

    authFetch(`/admin/analytics/city-overview?days=${days}`)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [days])

  return (
    <div className="flex flex-col gap-3">
      {/* Section subtitle */}
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
        Municipal Area Breakdown &nbsp;·&nbsp; each admin's zone
      </p>

      {/* 4-col card grid */}
      <div className="grid grid-cols-4 gap-4">
        {loading
          ? [0,1,2,3].map(i => <CardSkeleton key={i} />)
          : data?.cities?.length
            ? data.cities.map(c => <CityCard key={c.city} city={c} />)
            : <p className="text-sm text-gray-400 col-span-4">No city data available.</p>
        }
      </div>
    </div>
  )
}

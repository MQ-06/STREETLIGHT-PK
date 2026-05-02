// Module 6 — Super Admin city cards (warm beige, matches mockup layout)
import { useState, useEffect } from 'react'
import { authFetchJson } from '../../utils/auth'

const RISK = {
  HIGH: { bg: '#FEE2E2', text: '#DC2626', label: 'HIGH RISK' },
  MED:  { bg: '#FEF3C7', text: '#B45309', label: 'MED RISK'  },
  LOW:  { bg: '#DCFCE7', text: '#15803D', label: 'LOW RISK'  },
}

function MetricCell({ label, value, highlight }) {
  return (
    <div className="flex flex-col gap-0.5">
      <p className="text-xs text-gray-400 uppercase tracking-wide">{label}</p>
      <p className={`text-sm font-bold ${highlight ? 'text-red-500' : 'text-gray-800'}`}>
        {value ?? '—'}
      </p>
    </div>
  )
}

function CityCard({ city, onClick, periodDays }) {
  const risk = RISK[city.risk] ?? RISK.LOW
  const fDelta = city.forecast_delta
  const fSign  = fDelta > 0 ? '+' : ''
  const fColor = fDelta > 0 ? 'text-red-500' : fDelta < 0 ? 'text-green-600' : 'text-gray-400'

  return (
    <button
      onClick={() => onClick(city.city)}
      className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3 text-left hover:shadow-md hover:border-primary transition-all duration-200 w-full"
    >
      {/* Header — city name + risk badge */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-base font-black text-gray-900">{city.label}</p>
          {city.admin_name && (
            <p className="text-xs text-gray-400 mt-0.5">Admin: {city.admin_name}</p>
          )}
        </div>
        <span
          className="shrink-0 text-xs font-bold px-2 py-0.5 rounded-md"
          style={{ backgroundColor: risk.bg, color: risk.text }}
        >
          {risk.label}
        </span>
      </div>

      {/* 2×2 metrics grid */}
      <div className="grid grid-cols-2 gap-x-4 gap-y-2 pt-3 border-t border-warm-border">
        <MetricCell label="Reports"   value={city.total} />
        <MetricCell label="Avg Res."  value={`${city.avg_res_days}d`} highlight={city.avg_res_days > 7} />
        <MetricCell label="Re-report" value={`${city.re_rate}%`}      highlight={city.re_rate > 25} />
        <MetricCell label="Civic Score" value={city.civic_score} />
      </div>

      {/* Top issue */}
      {city.top_category && (
        <p className="text-xs text-gray-500">
          Top Issue: <span className="font-semibold text-gray-700">
            {city.top_category} ({city.top_cat_pct}%)
          </span>
        </p>
      )}

      {/* Bottleneck */}
      {city.bottleneck ? (
        <p className="text-xs text-amber-600 font-medium">
          {city.bottleneck}
          {city.bn_avg_days != null ? ` · ${city.bn_avg_days}d` : ''}
        </p>
      ) : (
        <p className="text-xs text-green-600 font-medium">No bottleneck</p>
      )}

      <div className="flex items-center justify-between pt-2 border-t border-warm-border">
        <p className="text-xs text-gray-400">{periodDays}d forecast</p>
        <p className={`text-xs font-bold ${fColor}`}>
          {fSign}{fDelta} reports →
        </p>
      </div>
    </button>
  )
}

function AggregateBanner({ agg }) {
  const metrics = [
    { label: 'Total Reports',  value: agg.total },
    { label: 'Pending',        value: agg.pending },
    { label: 'Avg Resolution', value: `${agg.avg_res_days}d` },
    { label: 'Re-report Rate', value: `${agg.re_rate}%` },
  ]
  return (
    <div className="bg-primary rounded-2xl p-5 grid grid-cols-4 gap-4">
      {metrics.map(m => (
        <div key={m.label} className="flex flex-col gap-1">
          <p className="text-xs font-medium text-orange-100 uppercase tracking-wide">{m.label}</p>
          <p className="text-2xl font-black text-white">{m.value}</p>
        </div>
      ))}
    </div>
  )
}

function CardSkeleton() {
  return <div className="h-56 bg-gray-100 rounded-2xl animate-pulse" />
}

export default function CityOverviewCards({ days, onCityClick }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    authFetchJson(`/admin/analytics/city-overview?days=${days}`)
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [days])

  if (loading) {
    return (
      <div className="flex flex-col gap-4">
        <div className="h-24 bg-gray-100 rounded-2xl animate-pulse" />
        <div className="grid grid-cols-2 gap-4">
          {[0, 1, 2, 3].map(i => <CardSkeleton key={i} />)}
        </div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <h2 className="text-base font-black text-gray-900">City Intelligence</h2>
        <span className="text-xs text-gray-400">— national overview · click a city to drill down</span>
      </div>

      {/* National aggregate banner */}
      <AggregateBanner agg={data.aggregate} />

      {/* Per-city cards */}
      {data.cities.length > 0 ? (
        <div className="grid grid-cols-2 gap-4">
          {data.cities.map(c => (
            <CityCard key={c.city} city={c} onClick={onCityClick} periodDays={days} />
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-400 text-center py-6">No city data available for this period.</p>
      )}
    </div>
  )
}

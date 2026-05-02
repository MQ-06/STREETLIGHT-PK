// Analytics page — smart router: super_admin → dark dashboard, others → shared warm dashboard
import SuperAdminAnalytics from './SuperAdminAnalytics'
import { useState, useRef } from 'react'
import { getRole, getCity, getDepartment } from '../../utils/auth'
import ScopeTabStrip    from '../../components/analytics/ScopeTabStrip'
import KpiRow           from '../../components/analytics/KpiRow'
import ChartRow         from '../../components/analytics/ChartRow'
import InsightRow       from '../../components/analytics/InsightRow'
import AlertsFeed       from '../../components/analytics/AlertsFeed'
import AnalyticsReportModal from '../../components/analytics/AnalyticsReportModal'
import RecommendationsModal from '../../components/analytics/RecommendationsModal'
import CityOverviewCards from '../../components/analytics/CityOverviewCards'

const DAYS_OPTIONS = [7, 30, 90]

function defaultScope(role, city, department) {
  if (role === 'super_admin') return { scope: 'national', scopeId: '' }
  if (role === 'city_admin')  return { scope: 'city',     scopeId: city || '' }
  const c = city || '', d = department || ''
  return { scope: 'city_dept', scopeId: c && d ? `${c}_${d}` : '' }
}

export default function Analytics() {
  const role       = getRole()

  // Super admin gets their own dark dashboard
  if (role === 'super_admin') return <SuperAdminAnalytics />

  const city       = getCity()
  const department = getDepartment()

  const def = defaultScope(role, city, department)
  const [scope,      setScope]      = useState(def.scope)
  const [scopeId,    setScopeId]    = useState(def.scopeId)
  const [days,       setDays]       = useState(30)
  const [forcedCity, setForcedCity] = useState(undefined)
  const [reportOpen, setReportOpen] = useState(false)
  const [recOpen, setRecOpen] = useState(false)

  const drillRef = useRef(null)

  function handleScopeChange(newScope, newScopeId) {
    setScope(newScope)
    setScopeId(newScopeId)
  }

  // Called when a city card is clicked — drills down into that city
  function handleCityClick(cityId) {
    setForcedCity(cityId)           // syncs ScopeTabStrip
    handleScopeChange('city', cityId)
    // Scroll to drill-down section smoothly
    setTimeout(() => drillRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
  }

  const isNational = scope === 'national'

  return (
    <div className="p-6 space-y-5">

      {/* ── Page header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-gray-900">
            {role === 'super_admin' ? 'Super Admin Dashboard' : 'Analytics'}
          </h1>
          <p className="text-sm text-gray-400 mt-0.5">
            {role === 'super_admin' ? 'City Intelligence · All Municipal Areas'
              : role === 'city_admin' ? `City: ${city}`
              : `Dept: ${department} · ${city}`}
          </p>
        </div>

        {/* Days filter */}
        <div className="flex gap-1 bg-white border border-warm-border rounded-xl p-1">
          {DAYS_OPTIONS.map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                days === d ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-800'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* ── Module 6 — City intelligence (super_admin only) ── */}
      {role === 'super_admin' && (
        <CityOverviewCards days={days} onCityClick={handleCityClick} />
      )}

      {/* ── Drill-down anchor ── */}
      <div ref={drillRef} />

      {/* ── Module 5 — Scope tab strip ── */}
      <ScopeTabStrip onSelect={handleScopeChange} forcedCity={forcedCity} />

      {/* ── Section label when drilling into a city ── */}
      {role === 'super_admin' && !isNational && (
        <div className="flex items-center gap-3">
          <button
            onClick={() => { handleScopeChange('national', ''); setForcedCity(null) }}
            className="text-xs text-primary font-semibold hover:underline"
          >
            ← Back to national
          </button>
          <span className="text-sm font-bold text-gray-700">
            {scopeId.split('_')[0].toUpperCase()} — City Analytics
          </span>
        </div>
      )}

      {/* ── Module 1 — KPI row ── */}
      <KpiRow scope={scope} scopeId={scopeId} days={days} />

      {/* ── Module 2 + 3 — Charts section ──
           National: 3 columns [Donut | Funnel | AI Cards]
           City/Dept: 2 columns [Donut | Funnel] then AI Cards below
      */}
      {isNational ? (
        <div className="grid grid-cols-3 gap-4 items-start">
          <div className="col-span-2">
            <ChartRow scope={scope} scopeId={scopeId} days={days} />
          </div>
          <InsightRow scope={scope} scopeId={scopeId} days={days} compact />
        </div>
      ) : (
        <>
          <ChartRow scope={scope} scopeId={scopeId} days={days} />
          <div id="insight-row">
            <InsightRow scope={scope} scopeId={scopeId} days={days} />
          </div>
        </>
      )}

      {/* ── Module 4 — Alerts + CTA ── */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <AlertsFeed scope={scope} scopeId={scopeId} days={days} />
        </div>
        <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3 justify-center">
          <p className="text-sm font-semibold text-gray-700">Quick Actions</p>
          <button
            type="button"
            onClick={() => setReportOpen(true)}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-dark transition-colors"
          >
            Generate report (PDF)
          </button>
          <button
            type="button"
            onClick={() => setRecOpen(true)}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border border-primary text-primary text-sm font-semibold hover:bg-orange-50 transition-colors"
          >
            View recommendations
          </button>
        </div>
      </div>

      <RecommendationsModal
        open={recOpen}
        onClose={() => setRecOpen(false)}
        scope={scope}
        scopeId={scopeId}
        days={days}
      />

      <AnalyticsReportModal
        open={reportOpen}
        onClose={() => setReportOpen(false)}
        scope={scope}
        scopeId={scopeId}
        days={days}
      />

    </div>
  )
}

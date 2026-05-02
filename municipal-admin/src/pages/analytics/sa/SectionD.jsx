// SA Module 5 — Section D: Alerts & Action Buttons
import { useState, useEffect } from 'react'
import { authFetchJson } from '../../../utils/auth'
import AnalyticsReportModal from '../../../components/analytics/AnalyticsReportModal'
import RecommendationsModal from '../../../components/analytics/RecommendationsModal'

// ── Alert type config ─────────────────────────────────────────────────────────
const TYPE_CONFIG = {
  area_warning:     { dot: '#EF4444', prefix: 'REPEAT REPORTS', bold: true  },
  anomaly:          { dot: '#EF4444', prefix: 'BUSY DAY',       bold: true  },
  predictive:       { dot: '#6366F1', prefix: 'FROM DATA',      bold: true  },
  dept_nudge:       { dot: '#F97316', prefix: 'SLOW TO CLOSE',  bold: false },
  seasonal:         { dot: '#6366F1', prefix: 'FROM DATA',      bold: true  },
  resource_suggest: { dot: '#3B82F6', prefix: 'WORKLOAD',       bold: false },
  ok:               { dot: '#22C55E', prefix: 'ALL CLEAR',      bold: false },
}

// Severity rank for sorting (lower = more urgent)
const SEVERITY_RANK = {
  anomaly:          0,
  predictive:       1,
  seasonal:         1,
  smart_city:       1,
  area_warning:     2,
  dept_nudge:       3,
  resource_suggest: 4,
  ok:               5,
}

// ── Single alert row ──────────────────────────────────────────────────────────
function AlertRow({ alert }) {
  const t = alert.type === 'smart_city' ? 'predictive' : alert.type
  const cfg = TYPE_CONFIG[t] ?? TYPE_CONFIG.ok

  return (
    <div className="flex items-start gap-3 py-3 border-b border-warm-border last:border-0">
      {/* Severity dot */}
      <span
        className="mt-0.5 shrink-0 w-2.5 h-2.5 rounded-full"
        style={{ background: cfg.dot }}
      />

      {/* Message */}
      <p className={`text-sm leading-snug ${cfg.bold ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
        <span
          className="text-xs font-bold mr-1.5 uppercase tracking-wide"
          style={{ color: cfg.dot }}
        >
          {cfg.prefix}:
        </span>
        {alert.message}
      </p>
    </div>
  )
}

// ── Alerts panel ──────────────────────────────────────────────────────────────
function AlertsPanel({ days }) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setData(null)

    authFetchJson(`/admin/analytics/alerts?scope=national&scope_id=&days=${days}`)
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [days])

  const rank = x => SEVERITY_RANK[x?.type === 'smart_city' ? 'predictive' : x?.type] ?? 9
  const sorted = [...(data?.alerts ?? [])].sort((a, b) => rank(a) - rank(b))

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3">
      {/* Header */}
      <div>
        <p className="text-sm font-bold text-gray-900">Predictive Alerts</p>
        <p className="text-xs text-gray-400 mt-0.5">
          Each line explains what your stored complaint numbers suggest — simplest words first.
        </p>
      </div>

      {/* Scrollable list */}
      <div className="overflow-y-auto" style={{ maxHeight: 280 }}>
        {loading ? (
          <div className="flex flex-col gap-3 py-2">
            {[0,1,2,3].map(i => (
              <div key={i} className="flex items-center gap-3 animate-pulse">
                <div className="w-2.5 h-2.5 rounded-full bg-gray-200 shrink-0" />
                <div className="h-3 bg-gray-100 rounded flex-1" />
              </div>
            ))}
          </div>
        ) : sorted.length === 0 ? (
          <p className="text-sm text-gray-400 py-4 text-center">No alerts for this period.</p>
        ) : (
          sorted.map((alert, i) => <AlertRow key={i} alert={alert} />)
        )}
      </div>
    </div>
  )
}

// ── Action buttons panel ──────────────────────────────────────────────────────
function ActionsPanel({ onOpenReport, onOpenRecommendations }) {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-4 justify-center">
      <p className="text-sm font-bold text-gray-900">Quick Actions</p>

      <button
        type="button"
        onClick={onOpenReport}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-bold text-white transition-opacity hover:opacity-90"
        style={{ background: '#E8612D' }}
      >
        Generate report (PDF)
      </button>

      <button
        type="button"
        onClick={onOpenRecommendations}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-bold transition-colors hover:bg-orange-50"
        style={{ border: '1.5px solid #E8612D', color: '#E8612D' }}
      >
        View recommendations
      </button>
    </div>
  )
}

// ── Section D ─────────────────────────────────────────────────────────────────
export default function SectionD({ days }) {
  const [reportOpen, setReportOpen] = useState(false)
  const [recOpen, setRecOpen] = useState(false)

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
        Alerts & Actions &nbsp;·&nbsp; cross-area signals + quick actions
      </p>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <AlertsPanel days={days} />
        </div>
        <ActionsPanel
          onOpenReport={() => setReportOpen(true)}
          onOpenRecommendations={() => setRecOpen(true)}
        />
      </div>

      <RecommendationsModal
        open={recOpen}
        onClose={() => setRecOpen(false)}
        scope="national"
        scopeId=""
        days={days}
      />

      <AnalyticsReportModal
        open={reportOpen}
        onClose={() => setReportOpen(false)}
        scope="national"
        scopeId=""
        days={days}
      />
    </div>
  )
}

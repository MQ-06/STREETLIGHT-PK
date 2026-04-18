// SA Module 5 — Section D: Alerts & Action Buttons
import { useState, useEffect } from 'react'
import { authFetch } from '../../../utils/auth'

// ── Alert type config ─────────────────────────────────────────────────────────
const TYPE_CONFIG = {
  area_warning:     { dot: '#EF4444', prefix: 'CRITICAL',    bold: true  },
  anomaly:          { dot: '#EF4444', prefix: 'ANOMALY',     bold: true  },
  dept_nudge:       { dot: '#F97316', prefix: 'ACTION',      bold: false },
  seasonal:         { dot: '#F59E0B', prefix: 'SEASONAL',    bold: false },
  resource_suggest: { dot: '#3B82F6', prefix: 'RESOURCE',    bold: false },
  ok:               { dot: '#22C55E', prefix: 'ALL CLEAR',   bold: false },
}

// Severity rank for sorting (lower = more urgent)
const SEVERITY_RANK = {
  anomaly:          0,
  area_warning:     1,
  dept_nudge:       2,
  seasonal:         3,
  resource_suggest: 4,
  ok:               5,
}

// ── Single alert row ──────────────────────────────────────────────────────────
function AlertRow({ alert }) {
  const cfg = TYPE_CONFIG[alert.type] ?? TYPE_CONFIG.ok

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

    authFetch(`/admin/analytics/alerts?scope=national&scope_id=&days=${days}`)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [days])

  const sorted = [...(data?.alerts ?? [])].sort(
    (a, b) => (SEVERITY_RANK[a.type] ?? 9) - (SEVERITY_RANK[b.type] ?? 9)
  )

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3">
      {/* Header */}
      <div>
        <p className="text-sm font-bold text-gray-900">Predictive Alerts & Recommendations</p>
        <p className="text-xs text-gray-400 mt-0.5">Cross-area insights ranked by severity</p>
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
function ActionsPanel() {
  function scrollToInsights() {
    // Section C contains the AI cards — scroll to it
    document.getElementById('sa-section-c')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-4 justify-center">
      <p className="text-sm font-bold text-gray-900">Quick Actions</p>

      {/* Generate Full Report */}
      <button
        onClick={() => window.print()}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-bold text-white transition-opacity hover:opacity-90"
        style={{ background: '#E8612D' }}
      >
        <span>🖨</span> Generate Full Report
      </button>

      {/* Get Recommendations */}
      <button
        onClick={scrollToInsights}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-bold transition-colors hover:bg-orange-50"
        style={{ border: '1.5px solid #E8612D', color: '#E8612D' }}
      >
        <span>💡</span> Get Recommendations
      </button>
    </div>
  )
}

// ── Section D ─────────────────────────────────────────────────────────────────
export default function SectionD({ days }) {
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
        Alerts & Actions &nbsp;·&nbsp; cross-area signals + quick actions
      </p>

      <div className="grid grid-cols-3 gap-4">
        {/* Alerts take 2/3 width */}
        <div className="col-span-2">
          <AlertsPanel days={days} />
        </div>

        {/* Action buttons take 1/3 */}
        <ActionsPanel />
      </div>
    </div>
  )
}

// Module 4 — Predictive Alerts Feed (5 rule-based types)
import { useState, useEffect } from 'react'
import { authFetch } from '../../utils/auth'

/**
 * Visual config for each alert type — matches the spec exactly:
 *   area_warning     → red
 *   resource_suggest → blue
 *   seasonal         → amber
 *   dept_nudge       → orange
 *   anomaly          → red bold
 *   ok               → green
 */
const TYPE_CONFIG = {
  area_warning: {
    dot:        '#EF4444',
    bg:         '#FEF2F2',
    badge:      'Area Warning',
    badgeBg:    '#FEE2E2',
    badgeText:  '#DC2626',
    icon:       '🚨',
    bold:       false,
  },
  resource_suggest: {
    dot:        '#3B82F6',
    bg:         '#EFF6FF',
    badge:      'Resource Suggestion',
    badgeBg:    '#DBEAFE',
    badgeText:  '#1D4ED8',
    icon:       '👥',
    bold:       false,
  },
  seasonal: {
    dot:        '#F59E0B',
    bg:         '#FFFBEB',
    badge:      'Seasonal Prediction',
    badgeBg:    '#FEF3C7',
    badgeText:  '#B45309',
    icon:       '🌧️',
    bold:       false,
  },
  dept_nudge: {
    dot:        '#F97316',
    bg:         '#FFF7ED',
    badge:      'Department Nudge',
    badgeBg:    '#FFEDD5',
    badgeText:  '#C2410C',
    icon:       '🎯',
    bold:       false,
  },
  anomaly: {
    dot:        '#DC2626',
    bg:         '#FEF2F2',
    badge:      'Anomaly Alert',
    badgeBg:    '#FEE2E2',
    badgeText:  '#991B1B',
    icon:       '⚡',
    bold:       true,
  },
  ok: {
    dot:        '#22C55E',
    bg:         '#F0FDF4',
    badge:      'All Clear',
    badgeBg:    '#DCFCE7',
    badgeText:  '#15803D',
    icon:       '✅',
    bold:       false,
  },
}

function AlertItem({ alert }) {
  const cfg = TYPE_CONFIG[alert.type] ?? TYPE_CONFIG.ok

  return (
    <div
      className="flex items-start gap-3 px-4 py-3 rounded-xl"
      style={{ backgroundColor: cfg.bg }}
    >
      {/* Coloured dot */}
      <span
        className="mt-1.5 shrink-0 w-2 h-2 rounded-full"
        style={{ backgroundColor: cfg.dot }}
      />

      {/* Icon + message */}
      <div className="flex-1 min-w-0">
        <span className="mr-1.5 text-sm">{cfg.icon}</span>
        <span
          className="text-sm text-gray-700"
          style={{ fontWeight: cfg.bold ? 700 : 400 }}
        >
          {alert.message}
        </span>
      </div>

      {/* Type badge */}
      <span
        className="shrink-0 text-xs font-semibold px-2 py-0.5 rounded-full whitespace-nowrap"
        style={{
          backgroundColor: cfg.badgeBg,
          color:           cfg.badgeText,
          border:          `1px solid ${cfg.dot}22`,
        }}
      >
        {cfg.badge}
      </span>
    </div>
  )
}

function SkeletonItem() {
  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gray-50 animate-pulse">
      <div className="w-2 h-2 rounded-full bg-gray-200 shrink-0" />
      <div className="flex-1 h-4 bg-gray-200 rounded" />
      <div className="w-28 h-5 bg-gray-200 rounded-full shrink-0" />
    </div>
  )
}

export default function AlertsFeed({ scope, scopeId, days }) {
  const [alerts,  setAlerts]  = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    const params = new URLSearchParams({ scope, scope_id: scopeId || '', days })
    authFetch(`/admin/analytics/alerts?${params}`)
      .then(r => r.json())
      .then(d => { if (!cancelled) { setAlerts(d.alerts ?? []); setLoading(false) } })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [scope, scopeId, days])

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">Predictive Alerts</h3>
        {!loading && (
          <span className="text-xs text-gray-400">
            {alerts.length} alert{alerts.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      <div className="flex flex-col gap-2 max-h-72 overflow-y-auto pr-1">
        {loading
          ? [0, 1, 2].map(i => <SkeletonItem key={i} />)
          : alerts.map((a, i) => <AlertItem key={i} alert={a} />)
        }
      </div>
    </div>
  )
}

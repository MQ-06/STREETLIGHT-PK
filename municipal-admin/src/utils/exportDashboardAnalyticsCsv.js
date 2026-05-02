
/**
 * Builds a CSV from GET /admin/dashboard/analytics — same scope rules as the dashboard
 * (city_admin → city; dept_officer → dept; super_admin → all).
 */
import { authFetchJson } from './auth'

function csvEscape(cell) {
  const s = String(cell ?? '')
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`
  return s
}

function rowsToCsv(rows) {
  return rows.map(row => row.map(csvEscape).join(',')).join('\n')
}

export async function downloadDashboardAnalyticsCsv(days) {
  const analytics = await authFetchJson(`/admin/dashboard/analytics?days=${days}`)
  const rows = [
    ['Metric', 'Value'],
    ['Days window', String(days)],
    ['Total reports (all time in DB snapshot)', String(analytics.total ?? 0)],
    ['Resolved (terminal stages)', String(analytics.resolved ?? 0)],
    [
      'Resolution rate',
      analytics.total ? `${((analytics.resolved / analytics.total) * 100).toFixed(1)}%` : '0%',
    ],
    [],
    ['--- Daily trend (complaints created per day in window) ---'],
    ['Date', 'New complaints'],
    ...(analytics.trend || []).map(t => [t.date, String(t.total)]),
    [],
    ['--- Category breakdown (all loaded reports) ---'],
    ['Category', 'Count'],
    ...Object.entries(analytics.category_breakdown || {}).map(([k, v]) => [k, String(v)]),
    [],
    ['--- Department breakdown ---'],
    ['Department', 'Total', 'Resolved'],
    ...Object.entries(analytics.dept_breakdown || {}).map(([d, t]) => [
      d,
      String(t),
      String(analytics.dept_resolved?.[d] ?? 0),
    ]),
    [],
    ['--- Stage distribution ---'],
    ['Stage', 'Count'],
    ...Object.entries(analytics.stage_distribution || {}).map(([s, c]) => [s, String(c)]),
  ]
  if (analytics.avg_resolution_hours != null) {
    rows.push([])
    rows.push(['Avg resolution (hours, resolved subset)', String(analytics.avg_resolution_hours)])
  }
  if (analytics.citizen_confirmation_rate_pct != null) {
    rows.push([
      'Citizen confirmation rate %',
      String(analytics.citizen_confirmation_rate_pct),
    ])
  }

  const csv = rowsToCsv(rows)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `streetlight-dashboard-analytics-${days}d.csv`
  a.click()
  URL.revokeObjectURL(url)
}

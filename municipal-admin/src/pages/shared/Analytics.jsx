import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Calendar, Download, MapPin, TrendingUp, TrendingDown } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch } from '../../utils/auth'

const CATEGORY_META = {
  STREETLIGHT:      { label: 'Streetlights',     color: '#B85C2E' },
  WASTE_MANAGEMENT: { label: 'Waste Management', color: '#EAB308' },
  ROAD_DAMAGE:      { label: 'Road & Potholes',  color: '#22C55E' },
  WATER_SUPPLY:     { label: 'Water Supply',      color: '#3B82F6' },
  OTHER:            { label: 'Other',             color: '#9CA3AF' },
}
const DEPT_COLORS = { lmc: '#B85C2E', lwmc: '#EAB308', fmc: '#3B82F6', fwmc: '#22C55E' }

function DonutChart({ slices }) {
  const r = 68, circ = 2 * Math.PI * r, gap = 3
  let off = 0
  const total = slices.reduce((s, x) => s + x.pct, 0) || 1
  const rendered = slices.map(s => {
    const pct = (s.pct / total) * 100
    const dash = (pct / 100) * circ - gap
    const sl = { ...s, dash, off: off }
    off += (pct / 100) * circ
    return sl
  })
  return (
    <svg width="176" height="176" viewBox="0 0 176 176">
      {rendered.map((s, i) => (
        <circle key={i} cx="88" cy="88" r={r} fill="none" stroke={s.color} strokeWidth="20"
          strokeDasharray={s.dash + ' ' + (circ - s.dash)}
          strokeDashoffset={-s.off + circ * 0.25} />
      ))}
      <text x="88" y="82"  textAnchor="middle" fontSize="22" fontWeight="800" fill="#111827">{slices.length > 0 ? String(slices.reduce((a, b) => a + b.pct, 0)) : '0'}</text>
      <text x="88" y="100" textAnchor="middle" fontSize="8"  fontWeight="600" fill="#9CA3AF" letterSpacing="1.5">TOTAL REPORTS</text>
    </svg>
  )
}

function TrendBars({ trend }) {
  if (!trend || trend.length === 0) return (
    <div className="flex items-end justify-center gap-1 h-24 text-xs text-gray-400">No trend data</div>
  )
  const maxVal = Math.max(...trend.map(t => t.total), 1)
  const recent = trend.slice(-14)
  return (
    <div className="flex items-end gap-1 h-24">
      {recent.map((t, i) => {
        const h = Math.max(4, Math.round((t.total / maxVal) * 96))
        return (
          <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
            <div
              className="w-full rounded-t-sm transition-all"
              style={{ height: h, backgroundColor: '#B85C2E', opacity: 0.75 }}
            />
            <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap pointer-events-none z-10">
              {t.date}: {t.total}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default function Analytics() {
  const navigate = useNavigate()
  const [days, setDays]           = useState(30)
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    setLoading(true)
    authFetch('/admin/dashboard/analytics?days=' + days)
      .then(r => r.json())
      .then(d => { setAnalytics(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [days])

  const total    = analytics?.total    ?? 0
  const resolved = analytics?.resolved ?? 0
  const resRate  = total ? ((resolved / total) * 100).toFixed(1) : '—'

  // Category breakdown → donut slices
  const catBreakdown = analytics?.category_breakdown || {}
  const catEntries   = Object.entries(catBreakdown).sort((a, b) => b[1] - a[1])
  const donutSlices  = catEntries.map(([key, count]) => ({
    label: (CATEGORY_META[key] || { label: key }).label,
    color: (CATEGORY_META[key] || { color: '#9CA3AF' }).color,
    pct:   count,
  }))

  // Dept breakdown
  const deptBreakdown = analytics?.dept_breakdown || {}
  const deptEntries   = Object.entries(deptBreakdown).sort((a, b) => b[1] - a[1])
  const deptMax       = Math.max(...deptEntries.map(d => d[1]), 1)

  const STATS = [
    { icon: '📋', iconBg: '#FFF7ED', label: 'Total Reports',   value: loading ? '…' : String(total),   change: null },
    { icon: '✅', iconBg: '#F0FDF4', label: 'Resolution Rate', value: loading ? '…' : resRate + '%',   change: null },
    { icon: '📥', iconBg: '#EFF6FF', label: 'New',             value: loading ? '…' : String(analytics?.stage_distribution?.NEW ?? 0),         change: null },
    { icon: '🔄', iconBg: '#FEF3E2', label: 'In Progress',     value: loading ? '…' : String(analytics?.stage_distribution?.IN_PROGRESS ?? 0), change: null },
  ]

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Analytics & Performance" subtitle="Real-time insights into municipal efficiency and public engagement.">
        <div className="flex items-center gap-1 bg-white border border-warm-border rounded-xl p-1 shadow-sm">
          {[7, 30, 90].map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={'px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ' + (days === d ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-800')}
            >
              {d}d
            </button>
          ))}
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark">
          <Download size={14} /> Export
        </button>
      </PageHeader>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        {STATS.map(s => (
          <div key={s.label} className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg" style={{ backgroundColor: s.iconBg }}>{s.icon}</div>
            <div>
              <p className="text-xs text-gray-400 mb-1">{s.label}</p>
              <p className="text-2xl font-black text-gray-900">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-gray-900">Daily Report Trend</h2>
          <span className="text-xs text-gray-400">Last {days} days</span>
        </div>
        <TrendBars trend={analytics?.trend} />
        <div className="flex justify-between mt-2">
          {analytics?.trend && analytics.trend.length > 0 && (
            <>
              <span className="text-xs text-gray-400">{analytics.trend[0]?.date}</span>
              <span className="text-xs text-gray-400">{analytics.trend[analytics.trend.length - 1]?.date}</span>
            </>
          )}
        </div>
      </div>

      {/* Breakdown + Dept */}
      <div className="flex gap-5">
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border shrink-0" style={{ width: 300 }}>
          <h2 className="text-base font-bold text-gray-900 mb-5">Complaint Breakdown</h2>
          <div className="flex justify-center mb-5">
            <DonutChart slices={donutSlices.length > 0 ? donutSlices : [{ label: 'No data', color: '#E5E7EB', pct: 1 }]} />
          </div>
          <div className="flex flex-col gap-3">
            {donutSlices.length > 0 ? donutSlices.map(b => (
              <div key={b.label} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: b.color }} />
                  <span className="text-sm text-gray-600">{b.label}</span>
                </div>
                <span className="text-sm font-bold text-gray-700">{b.pct}</span>
              </div>
            )) : (
              <p className="text-sm text-gray-400 text-center">No data for this period</p>
            )}
          </div>
        </div>

        <div className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <h2 className="text-base font-bold text-gray-900 mb-6">Complaints by Department</h2>
          {deptEntries.length > 0 ? (
            <div className="flex flex-col gap-5">
              {deptEntries.map(([dept, count]) => {
                const color = DEPT_COLORS[dept.toLowerCase()] || '#B85C2E'
                const pct   = Math.round((count / deptMax) * 100)
                return (
                  <div key={dept} className="cursor-pointer hover:opacity-70" onClick={() => navigate('/departments')}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-gray-700 uppercase">{dept}</span>
                      <span className="text-sm font-bold text-gray-800">{count} reports</span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{ width: pct + '%', backgroundColor: color }} />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="flex items-center justify-center h-32 text-sm text-gray-400">
              {loading ? 'Loading…' : 'No department data for this period'}
            </div>
          )}
        </div>
      </div>

      {/* Stage Distribution */}
      {analytics?.stage_distribution && (
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <h2 className="text-base font-bold text-gray-900 mb-5">Stage Distribution</h2>
          <div className="grid grid-cols-6 gap-3">
            {Object.entries(analytics.stage_distribution).map(([stage, count]) => {
              const STAGE_COLORS = {
                NEW: '#6B7280', PENDING_VERIFICATION: '#3B82F6', VERIFIED: '#F97316',
                IN_PROGRESS: '#F59E0B', AWAITING_FEEDBACK: '#8B5CF6', RESOLVED: '#22C55E',
              }
              const STAGE_LABELS = {
                NEW: 'New', PENDING_VERIFICATION: 'Pending', VERIFIED: 'Verified',
                IN_PROGRESS: 'In Progress', AWAITING_FEEDBACK: 'Awaiting', RESOLVED: 'Resolved',
              }
              const color = STAGE_COLORS[stage] || '#9CA3AF'
              return (
                <div
                  key={stage}
                  className="flex flex-col items-center gap-2 p-4 rounded-2xl cursor-pointer hover:opacity-80"
                  style={{ backgroundColor: color + '18' }}
                  onClick={() => navigate('/complaint-management')}
                >
                  <span className="text-2xl font-black" style={{ color }}>{count}</span>
                  <span className="text-xs font-semibold text-gray-500 text-center">{STAGE_LABELS[stage] || stage}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

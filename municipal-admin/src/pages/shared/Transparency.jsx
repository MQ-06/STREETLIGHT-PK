import { useState, useEffect } from 'react'
import { ClipboardList, CheckCircle, CalendarDays, Building2, Activity } from 'lucide-react'
import { authFetchJson } from '../../utils/auth'
import PageHeader from '../../components/PageHeader'

const CITY_META = {
  lahore:     { label: 'Lahore',     depts: ['LMC', 'LWMC'] },
  faisalabad: { label: 'Faisalabad', depts: ['FMC', 'FWMC'] },
}

const STAGE_LABELS = {
  NEW: 'New', PENDING_VERIFICATION: 'Pending', VERIFIED: 'Verified',
  IN_PROGRESS: 'In Progress', AWAITING_FEEDBACK: 'Awaiting', RESOLVED: 'Resolved',
  CLOSED: 'Closed',
}
const STAGE_COLORS = {
  NEW: '#6B7280', PENDING_VERIFICATION: '#3B82F6', VERIFIED: '#F97316',
  IN_PROGRESS: '#F59E0B', AWAITING_FEEDBACK: '#8B5CF6', RESOLVED: '#22C55E',
  CLOSED: '#15803D',
}

function StatCard({ icon, label, value, sub, color }) {
  return (
    <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex flex-col gap-3">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center"
           style={{ backgroundColor: (color || '#B85C2E') + '18', color: color || '#B85C2E' }}>{icon}</div>
      <div>
        <p className="text-xs text-gray-400 mb-1">{label}</p>
        <p className="text-2xl font-black text-gray-900">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
      </div>
    </div>
  )
}

export default function Transparency() {
  const [data30,    setData30]    = useState(null)
  const [dataAll,   setDataAll]   = useState(null)
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    Promise.all([
      authFetchJson('/admin/dashboard/analytics?days=30'),
      authFetchJson('/admin/dashboard/analytics?days=365'),
    ]).then(([d30, d365]) => {
      setData30(d30)
      setDataAll(d365)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const total    = dataAll?.total    ?? 0
  const resolved = dataAll?.resolved ?? 0
  const resRate  = total ? ((resolved / total) * 100).toFixed(1) : '0'
  const stageDist = dataAll?.stage_distribution || {}
  const deptBreak = dataAll?.dept_breakdown     || {}
  const deptRes   = dataAll?.dept_resolved      || {}
  const catBreak  = dataAll?.category_breakdown || {}

  // Dept performance rows
  const deptRows = Object.entries(deptBreak).map(([dept, total]) => ({
    dept:     dept.toUpperCase(),
    total,
    resolved: deptRes[dept] || 0,
    rate:     total ? Math.round(((deptRes[dept] || 0) / total) * 100) : 0,
  })).sort((a, b) => b.total - a.total)

  // Category rows
  const catRows = Object.entries(catBreak).sort((a, b) => b[1] - a[1])
  const catTotal = catRows.reduce((s, [, v]) => s + v, 0) || 1

  const last30Total    = data30?.total    ?? 0
  const last30Resolved = data30?.resolved ?? 0

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader
        title="Transparency Portal"
        subtitle="Public performance metrics — municipal accountability at a glance."
      >
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-bold"
             style={{ backgroundColor: '#F0FDF4', color: '#22C55E' }}>
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" /> Live Data
        </div>
      </PageHeader>

      {/* Top KPIs */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={<ClipboardList size={18} />} label="Total Reports (All Time)" color="#B85C2E"
          value={loading ? '…' : String(total)}
          sub="submitted by citizens" />
        <StatCard icon={<CheckCircle size={18} />} label="Issues Resolved" color="#22C55E"
          value={loading ? '…' : String(resolved)}
          sub={loading ? '' : resRate + '% resolution rate'} />
        <StatCard icon={<CalendarDays size={18} />} label="Reports This Month" color="#3B82F6"
          value={loading ? '…' : String(last30Total)}
          sub={loading ? '' : last30Resolved + ' resolved'} />
        <StatCard icon={<Building2 size={18} />} label="Cities Covered" color="#8B5CF6"
          value="2"
          sub="Lahore · Faisalabad" />
      </div>

      {/* Resolution Rate Banner */}
      <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-gray-900">Overall Resolution Rate</h2>
          <span className="text-2xl font-black" style={{ color: '#22C55E' }}>{resRate}%</span>
        </div>
        <div className="h-3 rounded-full bg-gray-100 overflow-hidden">
          <div className="h-full rounded-full transition-all"
               style={{ width: resRate + '%', background: 'linear-gradient(90deg,#22C55E,#16A34A)' }} />
        </div>
        <div className="flex justify-between mt-2 text-xs text-gray-400">
          <span>0%</span><span>Target: 80%</span><span>100%</span>
        </div>
      </div>

      <div className="flex gap-5">
        {/* Stage Distribution */}
        <div className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <h2 className="text-base font-bold text-gray-900 mb-5">Current Pipeline Status</h2>
          {loading ? (
            <p className="text-sm text-gray-400">Loading…</p>
          ) : (
            <div className="flex flex-col gap-3">
              {Object.entries(stageDist).map(([stage, count]) => {
                const pct   = total ? Math.round((count / total) * 100) : 0
                const color = STAGE_COLORS[stage] || '#9CA3AF'
                return (
                  <div key={stage}>
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                        <span className="text-sm text-gray-700">{STAGE_LABELS[stage] || stage}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-gray-800">{count}</span>
                        <span className="text-xs text-gray-400 w-8 text-right">{pct}%</span>
                      </div>
                    </div>
                    <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: pct + '%', backgroundColor: color }} />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Issue Breakdown */}
        <div className="w-64 bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <h2 className="text-base font-bold text-gray-900 mb-5">Issue Types</h2>
          {loading ? <p className="text-sm text-gray-400">Loading…</p> : (
            <div className="flex flex-col gap-4">
              {catRows.map(([cat, count]) => {
                const pct   = Math.round((count / catTotal) * 100)
                const label = cat.replace('_', ' ').split(' ').map(w => w[0].toUpperCase() + w.slice(1).toLowerCase()).join(' ')
                const color = cat === 'POTHOLE' ? '#B85C2E' : cat === 'TRASH' ? '#EAB308' : '#9CA3AF'
                return (
                  <div key={cat}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm text-gray-700">{label}</span>
                      <span className="text-sm font-bold text-gray-800">{pct}%</span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: pct + '%', backgroundColor: color }} />
                    </div>
                  </div>
                )
              })}
              {catRows.length === 0 && <p className="text-sm text-gray-400">No data</p>}
            </div>
          )}
        </div>
      </div>

      {/* Dept Performance Table */}
      <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
        <h2 className="text-base font-bold text-gray-900 mb-5">Department Performance</h2>
        {loading ? (
          <p className="text-sm text-gray-400">Loading…</p>
        ) : deptRows.length === 0 ? (
          <p className="text-sm text-gray-400">No department data yet.</p>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                {['Department', 'Total Reports', 'Resolved', 'Resolution Rate', 'Performance'].map(h => (
                  <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 pb-3 pr-6">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {deptRows.map(row => {
                const perf  = row.rate >= 75 ? { label: 'Excellent', color: '#22C55E', bg: '#F0FDF4' }
                            : row.rate >= 50 ? { label: 'Good',      color: '#F59E0B', bg: '#FFFBEB' }
                            : row.rate >= 25 ? { label: 'Fair',      color: '#F97316', bg: '#FFF7ED' }
                            :                  { label: 'Needs Work',color: '#EF4444', bg: '#FEF2F2' }
                return (
                  <tr key={row.dept} className="border-b last:border-0">
                    <td className="py-4 pr-6">
                      <span className="text-sm font-bold text-gray-900">{row.dept}</span>
                    </td>
                    <td className="py-4 pr-6 text-sm text-gray-600">{row.total}</td>
                    <td className="py-4 pr-6 text-sm font-semibold" style={{ color: '#22C55E' }}>{row.resolved}</td>
                    <td className="py-4 pr-6">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-1.5 rounded-full bg-gray-100 overflow-hidden">
                          <div className="h-full rounded-full bg-primary" style={{ width: row.rate + '%' }} />
                        </div>
                        <span className="text-sm font-bold text-gray-700">{row.rate}%</span>
                      </div>
                    </td>
                    <td className="py-4">
                      <span className="text-xs font-bold px-2.5 py-1 rounded-full"
                            style={{ backgroundColor: perf.bg, color: perf.color }}>
                        {perf.label}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* City Cards */}
      <div className="grid grid-cols-2 gap-5">
        {Object.entries(CITY_META).map(([cityKey, meta]) => {
          const cityDepts = meta.depts
          const cityTotal = cityDepts.reduce((s, d) => s + (deptBreak[d.toLowerCase()] || 0), 0)
          const cityRes   = cityDepts.reduce((s, d) => s + (deptRes[d.toLowerCase()] || 0), 0)
          const cityRate  = cityTotal ? Math.round((cityRes / cityTotal) * 100) : 0
          return (
            <div key={cityKey} className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}>
                  <Building2 size={18} />
                </div>
                <div>
                  <h3 className="text-base font-bold text-gray-900">{meta.label}</h3>
                  <p className="text-xs text-gray-400">{meta.depts.join(' · ')}</p>
                </div>
                <div className="ml-auto text-right">
                  <p className="text-xl font-black" style={{ color: '#22C55E' }}>{cityRate}%</p>
                  <p className="text-xs text-gray-400">resolved</p>
                </div>
              </div>
              <div className="h-2 rounded-full bg-gray-100 overflow-hidden mb-3">
                <div className="h-full rounded-full bg-primary" style={{ width: cityRate + '%' }} />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>{cityTotal} total reports</span>
                <span>{cityRes} resolved</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

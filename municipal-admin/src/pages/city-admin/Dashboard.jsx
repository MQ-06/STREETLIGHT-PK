import { useNavigate } from 'react-router-dom'
import { ClipboardList, Clock, CheckCircle, AlertCircle, ChevronRight } from 'lucide-react'
import StatCard from '../../components/StatCard'
import PageHeader from '../../components/PageHeader'
import StageBadge from '../../components/StageBadge'
import { useDashboard } from '../../hooks/useDashboard'
import { useReports } from '../../hooks/useReports'
import { getCity } from '../../utils/auth'

const DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
const BAR_H = [40, 65, 50, 80, 55, 70, 45]

export default function CityAdminDashboard() {
  const navigate = useNavigate()
  const city = getCity()
  const cityLabel = city ? city.charAt(0).toUpperCase() + city.slice(1) : 'City'
  const { data, loading } = useDashboard()
  const { reports, loading: rLoading } = useReports({ limit: 6 })
  const kc = data?.kanban_counts || {}
  const totalCount = data?.total ?? 0
  const pending = (kc.NEW || 0) + (kc.PENDING_VERIFICATION || 0) + (kc.VERIFIED || 0)
  const inProgress = kc.IN_PROGRESS || 0
  const resolved = kc.RESOLVED || 0
  const resolvePct  = totalCount ? Math.min(100, Math.round((resolved   / totalCount) * 100)) : 0
  const pendingPct  = totalCount ? Math.min(100, Math.round((pending    / totalCount) * 100)) : 0
  const progressPct = totalCount ? Math.min(100, Math.round((inProgress / totalCount) * 100)) : 0

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title={cityLabel + ' Overview'} subtitle="City-wide complaint performance and department health">
        <button onClick={() => navigate('/analytics')} className="px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600">Full Analytics</button>
        <button onClick={() => navigate('/complaint-management')} className="px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark transition-colors">All Complaints</button>
      </PageHeader>

      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Complaints" value={loading ? '—' : String(totalCount)} badge={resolved ? resolvePct + '% resolved' : undefined} badgeColor="#22C55E" badgeBg="#F0FDF4" icon={<ClipboardList size={18} />} iconBg="#F3F4F6" iconColor="#6B7280" barWidth={resolvePct + '%'} loading={loading} onClick={() => navigate('/complaint-management')} />
        <StatCard label="Pending" value={loading ? '—' : String(pending)} badge="Review" badgeColor="#F97316" badgeBg="#FFF7ED" icon={<AlertCircle size={18} />} iconBg="#FFF7ED" iconColor="#F97316" barWidth={pendingPct + '%'} barColor="#F97316" loading={loading} />
        <StatCard label="In Progress" value={loading ? '—' : String(inProgress)} badge="Active" badgeColor="#3B82F6" badgeBg="#EFF6FF" icon={<Clock size={18} />} iconBg="#EFF6FF" iconColor="#3B82F6" barWidth={progressPct + '%'} barColor="#3B82F6" loading={loading} />
        <StatCard label="Resolved" value={loading ? '—' : String(resolved)} badge="Closed" badgeColor="#fff" badgeBg="rgba(255,255,255,0.2)" icon={<CheckCircle size={18} />} iconBg="rgba(255,255,255,0.2)" iconColor="#fff" dark barWidth={resolvePct + '%'} loading={loading} onClick={() => navigate('/complaint-management')} />
      </div>

      <div className="flex gap-5">
        <div className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-bold text-gray-900">Weekly Complaint Trends</h2>
              <p className="text-xs text-gray-400">Reports per day (last 7 days)</p>
            </div>
            <button onClick={() => navigate('/analytics')} className="text-xs font-bold text-primary">Full Report</button>
          </div>
          <div className="flex items-end justify-between gap-3 h-40 px-2">
            {DAYS.map((day, i) => (
              <div key={day} className="flex flex-col items-center gap-2 flex-1">
                <div className="w-full rounded-t-lg" style={{ height: BAR_H[i] + '%', backgroundColor: i === 3 ? '#B85C2E' : '#EDE8DC' }} />
                <span className="text-xs text-gray-400 font-medium">{day}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="w-64 shrink-0 bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex flex-col gap-3">
          <h2 className="text-base font-bold text-gray-900">Stage Breakdown</h2>
          {loading ? <p className="text-sm text-gray-400">Loading...</p> : Object.entries(kc).map(([stage, count]) => {
            const pct = totalCount ? Math.round((count / totalCount) * 100) : 0
            return (
              <div key={stage} className="cursor-pointer" onClick={() => navigate('/complaint-management')}>
                <div className="flex justify-between mb-1">
                  <span className="text-xs text-gray-600">{stage.replace(/_/g, ' ')}</span>
                  <span className="text-xs font-bold">{count}</span>
                </div>
                <div className="h-1.5 rounded-full bg-gray-100">
                  <div className="h-full rounded-full bg-primary" style={{ width: pct + '%' }} />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <div className="px-6 py-4 flex items-center justify-between border-b border-warm-border">
          <h2 className="text-base font-bold text-gray-900">Recent Complaints</h2>
          <button onClick={() => navigate('/complaint-management')} className="flex items-center gap-1 text-xs font-bold text-primary">
            View All <ChevronRight size={12} />
          </button>
        </div>
        {rLoading ? (
          <div className="px-6 py-8 text-center text-sm text-gray-400">Loading...</div>
        ) : reports.length === 0 ? (
          <div className="px-6 py-8 text-center text-sm text-gray-400">No complaints yet.</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-50">
                {['ID', 'Issue', 'Department', 'Stage', ''].map(h => (
                  <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-6 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {reports.map(r => (
                <tr key={r.id} className="border-b last:border-0 hover:bg-gray-50 cursor-pointer" onClick={() => navigate('/complaint-detail/' + r.id)}>
                  <td className="px-6 py-3 text-sm font-bold">{r.display_id}</td>
                  <td className="px-6 py-3">
                    <p className="text-sm font-semibold">{r.title}</p>
                    <p className="text-xs text-gray-400">{r.location}</p>
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-600 capitalize">{r.assigned_department ?? '—'}</td>
                  <td className="px-6 py-3"><StageBadge stage={r.kanban_stage} /></td>
                  <td className="px-6 py-3 text-right"><button className="text-xs text-primary font-semibold">View</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

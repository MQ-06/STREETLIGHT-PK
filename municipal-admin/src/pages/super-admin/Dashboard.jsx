import { useNavigate } from 'react-router-dom'
import { ClipboardList, Clock, CheckCircle, AlertCircle, Globe } from 'lucide-react'
import StatCard from '../../components/StatCard'
import PageHeader from '../../components/PageHeader'
import StageBadge from '../../components/StageBadge'
import { useDashboard } from '../../hooks/useDashboard'
import { useReports } from '../../hooks/useReports'

const CITIES = [
  { name: 'Lahore',     depts: ['LMC', 'LWMC'] },
  { name: 'Faisalabad', depts: ['FMC', 'FWMC'] },
]
const DAYS  = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
const BAR_H = [35, 60, 45, 85, 50, 65, 40]

export default function SuperAdminDashboard() {
  const navigate = useNavigate()
  const { data, loading }              = useDashboard()
  const { reports, loading: rLoading } = useReports({ limit: 8 })

  const kc         = data?.kanban_counts || {}
  const totalCount = data?.total ?? 0
  const pending    = (kc.NEW || 0) + (kc.PENDING_VERIFICATION || 0) + (kc.VERIFIED || 0)
  const inProgress = kc.IN_PROGRESS || 0
  const resolved   = kc.RESOLVED || 0

  const resolvePct  = totalCount ? Math.min(100, Math.round((resolved   / totalCount) * 100)) : 0
  const pendingPct  = totalCount ? Math.min(100, Math.round((pending    / totalCount) * 100)) : 0
  const progressPct = totalCount ? Math.min(100, Math.round((inProgress / totalCount) * 100)) : 0

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Pakistan Overview" subtitle="System-wide complaint performance across all cities">
        <button
          onClick={() => navigate('/departments')}
          className="px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600"
        >
          Departments
        </button>
        <button
          onClick={() => navigate('/complaint-management')}
          className="px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark transition-colors"
        >
          All Complaints
        </button>
      </PageHeader>

      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Total Complaints"
          value={loading ? '—' : String(totalCount)}
          badge={resolved ? resolvePct + '% resolved' : undefined}
          badgeColor="#22C55E" badgeBg="#F0FDF4"
          icon={<Globe size={18} />}
          iconBg="#F3F4F6" iconColor="#6B7280"
          barWidth={resolvePct + '%'}
          loading={loading}
          onClick={() => navigate('/complaint-management')}
        />
        <StatCard
          label="Pending"
          value={loading ? '—' : String(pending)}
          badge="Review"
          badgeColor="#F97316" badgeBg="#FFF7ED"
          icon={<AlertCircle size={18} />}
          iconBg="#FFF7ED" iconColor="#F97316"
          barWidth={pendingPct + '%'} barColor="#F97316"
          loading={loading}
        />
        <StatCard
          label="In Progress"
          value={loading ? '—' : String(inProgress)}
          badge="Active"
          badgeColor="#3B82F6" badgeBg="#EFF6FF"
          icon={<Clock size={18} />}
          iconBg="#EFF6FF" iconColor="#3B82F6"
          barWidth={progressPct + '%'} barColor="#3B82F6"
          loading={loading}
        />
        <StatCard
          label="Resolved"
          value={loading ? '—' : String(resolved)}
          badge="Closed"
          badgeColor="#fff" badgeBg="rgba(255,255,255,0.2)"
          icon={<CheckCircle size={18} />}
          iconBg="rgba(255,255,255,0.2)" iconColor="#fff"
          dark
          barWidth={resolvePct + '%'}
          loading={loading}
          onClick={() => navigate('/complaint-management')}
        />
      </div>

      <div className="flex gap-5">
        <div className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-warm-border transition-all hover:shadow-md">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-bold text-gray-900">System Trends</h2>
              <p className="text-xs text-gray-400">Nationwide reports per day (last 7 days)</p>
            </div>
            <button onClick={() => navigate('/analytics')} className="text-xs font-bold text-primary">Analytics</button>
          </div>
          <div className="flex items-end justify-between gap-3 h-40 px-2">
            {DAYS.map((day, i) => (
              <div key={day} className="flex flex-col items-center gap-2 flex-1">
                <div
                  className="w-full rounded-t-lg"
                  style={{ height: BAR_H[i] + '%', backgroundColor: i === 3 ? '#B85C2E' : '#EDE8DC' }}
                />
                <span className="text-xs text-gray-400 font-medium">{day}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="w-72 shrink-0 bg-white rounded-3xl p-5 shadow-sm border border-warm-border transition-all hover:shadow-md">
          <h2 className="text-base font-bold text-gray-900 mb-4">City Breakdown</h2>
          {CITIES.map(c => (
            <div key={c.name} className="mb-4 last:mb-0">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-semibold text-gray-800">{c.name}</span>
                <div className="flex gap-1">
                  {c.depts.map(d => (
                    <span
                      key={d}
                      className="text-xs font-bold px-2 py-0.5 rounded-full"
                      style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}
                    >
                      {d}
                    </span>
                  ))}
                </div>
              </div>
              <div className="h-1.5 rounded-full bg-gray-100">
                <div className="h-full rounded-full bg-primary" style={{ width: '50%' }} />
              </div>
            </div>
          ))}
          <button
            onClick={() => navigate('/departments')}
            className="mt-4 w-full py-2 rounded-xl text-xs font-bold text-primary border border-warm-border hover:bg-gray-50"
          >
            Manage Departments
          </button>
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden transition-all hover:shadow-md">
        <div className="px-6 py-4 flex items-center justify-between border-b border-warm-border bg-gray-50/50">
          <h2 className="text-base font-bold text-gray-900">Recent Complaints</h2>
          <button onClick={() => navigate('/complaint-management')} className="text-xs font-bold text-primary hover:underline">
            View All
          </button>
        </div>
        {rLoading ? (
          <div className="px-6 py-4 flex flex-col gap-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="w-full h-12 bg-gray-100 animate-pulse rounded-2xl"></div>
            ))}
          </div>
        ) : reports.length === 0 ? (
          <div className="px-6 py-8 text-center text-sm text-gray-400">No complaints yet.</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50/50">
              <tr className="border-b border-gray-100">
                {['ID', 'Issue', 'City', 'Department', 'Stage', ''].map(h => (
                  <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-6 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {reports.map(r => (
                <tr
                  key={r.id}
                  className="border-b last:border-0 hover:bg-gray-50 cursor-pointer"
                  onClick={() => navigate('/complaint-detail/' + r.id)}
                >
                  <td className="px-6 py-3 text-sm font-bold">{r.display_id}</td>
                  <td className="px-6 py-3">
                    <p className="text-sm font-semibold">{r.title}</p>
                    <p className="text-xs text-gray-400">{r.location}</p>
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-600 capitalize">{r.assigned_city ?? '—'}</td>
                  <td className="px-6 py-3 text-sm text-gray-600 uppercase">{r.assigned_department ?? '—'}</td>
                  <td className="px-6 py-3"><StageBadge stage={r.kanban_stage} /></td>
                  <td className="px-6 py-3 text-right">
                    <button className="text-xs text-primary font-semibold">View</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

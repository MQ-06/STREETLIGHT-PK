import { useNavigate } from 'react-router-dom'
import { ClipboardList, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import StatCard from '../../components/StatCard'
import PageHeader from '../../components/PageHeader'
import StageBadge from '../../components/StageBadge'
import { useDashboard } from '../../hooks/useDashboard'
import { useReports } from '../../hooks/useReports'
import { getDepartment, getCity } from '../../utils/auth'
import { DEPT_LABEL } from '../../utils/theme'

export default function DeptOfficerDashboard() {
  const navigate  = useNavigate()
  const dept      = getDepartment()
  const city      = getCity()
  const deptLabel = dept ? (DEPT_LABEL[dept] || dept.toUpperCase()) : 'Department'

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
      <PageHeader
        title="My Department Dashboard"
        subtitle={deptLabel + (city ? ' · ' + city.charAt(0).toUpperCase() + city.slice(1) : '')}
      >
        <button
          onClick={() => navigate('/complaint-management')}
          className="px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark transition-colors"
        >
          View All Complaints
        </button>
      </PageHeader>

      <div className="grid grid-cols-4 gap-4">
        <StatCard
          label="Total Assigned"
          value={loading ? '—' : String(totalCount)}
          icon={<ClipboardList size={18} />}
          iconBg="#F3F4F6" iconColor="#6B7280"
          barWidth={resolvePct + '%'}
          loading={loading}
          onClick={() => navigate('/complaint-management')}
        />
        <StatCard
          label="Pending Review"
          value={loading ? '—' : String(pending)}
          badge="Needs Action"
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
          badge="Goal"
          badgeColor="#fff" badgeBg="rgba(255,255,255,0.2)"
          icon={<CheckCircle size={18} />}
          iconBg="rgba(255,255,255,0.2)" iconColor="#fff"
          dark
          barWidth={resolvePct + '%'}
          loading={loading}
        />
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <div className="px-6 py-4 flex items-center justify-between border-b border-warm-border">
          <h2 className="text-base font-bold text-gray-900">Recent Complaints</h2>
          <button
            onClick={() => navigate('/complaint-management')}
            className="text-xs font-bold text-primary hover:underline"
          >
            View All
          </button>
        </div>
        {rLoading ? (
          <div className="px-6 py-10 text-center text-sm text-gray-400">Loading…</div>
        ) : reports.length === 0 ? (
          <div className="px-6 py-10 text-center text-sm text-gray-400">No complaints assigned yet.</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-50">
                {['ID', 'Issue', 'Severity', 'Stage', ''].map(h => (
                  <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-6 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {reports.map(r => (
                <tr
                  key={r.id}
                  className="border-b last:border-0 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => navigate('/complaint-detail/' + r.id)}
                >
                  <td className="px-6 py-3 text-sm font-bold text-gray-800">{r.display_id}</td>
                  <td className="px-6 py-3">
                    <p className="text-sm font-semibold text-gray-800">{r.title}</p>
                    <p className="text-xs text-gray-400">{r.location}</p>
                  </td>
                  <td className="px-6 py-3">
                    <span
                      className="text-xs font-bold px-2.5 py-1 rounded-full"
                      style={{ backgroundColor: r.severity_bg, color: r.severity_color }}
                    >
                      {r.severity}
                    </span>
                  </td>
                  <td className="px-6 py-3"><StageBadge stage={r.kanban_stage} /></td>
                  <td className="px-6 py-3 text-right">
                    <button className="text-xs text-primary font-semibold hover:underline">View</button>
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

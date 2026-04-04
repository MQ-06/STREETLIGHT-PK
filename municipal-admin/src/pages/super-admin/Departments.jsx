import { useNavigate } from 'react-router-dom'
import { Building2, Users, CheckCircle } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import EmptyState from '../../components/EmptyState'

const ROUTING_TABLE = [
  { city: 'Lahore',     dept: 'LMC',  deptFull: 'Lahore Metropolitan Corp.',   issueTypes: ['road', 'pothole', 'infrastructure'], officer: 'LMC Officer', active: true  },
  { city: 'Lahore',     dept: 'LWMC', deptFull: 'Lahore Waste Management Co.', issueTypes: ['garbage', 'trash', 'waste'],          officer: 'LWMC Officer', active: true },
  { city: 'Faisalabad', dept: 'FMC',  deptFull: 'Faisalabad Metropolitan Corp.', issueTypes: ['road', 'pothole', 'infrastructure'], officer: 'FMC Officer', active: true },
  { city: 'Faisalabad', dept: 'FWMC', deptFull: 'Faisalabad Waste Mgmt. Co.', issueTypes: ['garbage', 'trash', 'waste'],            officer: 'FWMC Officer', active: true },
]

export default function SuperAdminDepartments() {
  const navigate = useNavigate()

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Department Management" subtitle="Configure city-department routing and officer assignments.">
        <button
          onClick={() => navigate('/user-roles')}
          className="px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600"
        >
          <Users size={14} className="inline mr-1.5" />
          User Roles
        </button>
      </PageHeader>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center gap-4">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#FFF3EB' }}>
            <Building2 size={18} style={{ color: '#B85C2E' }} />
          </div>
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Active Depts</p>
            <p className="text-3xl font-black text-gray-900">4</p>
          </div>
        </div>
        <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center gap-4">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#F0FDF4' }}>
            <CheckCircle size={18} style={{ color: '#22C55E' }} />
          </div>
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Cities Covered</p>
            <p className="text-3xl font-black text-gray-900">2</p>
          </div>
        </div>
        <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center gap-4">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#EFF6FF' }}>
            <Users size={18} style={{ color: '#3B82F6' }} />
          </div>
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Assigned Officers</p>
            <p className="text-3xl font-black text-gray-900">4</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <div className="px-6 py-4 border-b border-warm-border">
          <h2 className="text-base font-bold text-gray-900">Routing Table</h2>
          <p className="text-xs text-gray-400 mt-0.5">Complaint auto-routing configuration</p>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-50">
              {['City', 'Department', 'Full Name', 'Issue Types', 'Officer', 'Status'].map(h => (
                <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-6 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROUTING_TABLE.map((row, i) => (
              <tr key={i} className="border-b last:border-0 hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-semibold text-gray-800 capitalize">{row.city}</td>
                <td className="px-6 py-4">
                  <span
                    className="text-xs font-bold px-2.5 py-1 rounded-full"
                    style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}
                  >
                    {row.dept}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{row.deptFull}</td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {row.issueTypes.map(t => (
                      <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 capitalize">{t}</span>
                    ))}
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{row.officer}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: row.active ? '#22C55E' : '#9CA3AF' }} />
                    <span className="text-xs font-medium" style={{ color: row.active ? '#22C55E' : '#9CA3AF' }}>
                      {row.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <EmptyState
        icon="⚙️"
        title="Department CRUD Coming Soon"
        description="Add, edit, and deactivate departments and routing rules from this panel."
        phase={3}
      />
    </div>
  )
}

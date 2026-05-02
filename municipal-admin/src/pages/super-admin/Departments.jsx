import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Users, CheckCircle } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetchJson } from '../../utils/auth'

export default function SuperAdminDepartments({ embedded = false } = {}) {
  const navigate = useNavigate()
  const [rows,    setRows]    = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    authFetchJson('/admin/routing')
      .then(d => { setRows(d.routing || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const activeDepts  = rows.filter(r => r.is_active).length
  const cities       = [...new Set(rows.map(r => r.city))].length
  const officersSet  = new Set(rows.filter(r => r.is_active && r.officer_id).map(r => r.officer_id))

  const shell = embedded ? 'flex flex-col gap-6' : 'p-6 flex flex-col gap-6'

  return (
    <div className={shell}>
      <PageHeader title="Department Management" subtitle="City-department routing and officer assignments.">
        {!embedded && (
          <button
            onClick={() => navigate('/organization?tab=users')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600"
          >
            <Users size={14} />
            User Roles
          </button>
        )}
      </PageHeader>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center gap-4">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#FFF3EB' }}>
            <Building2 size={18} style={{ color: '#B85C2E' }} />
          </div>
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Active Depts</p>
            <p className="text-3xl font-black text-gray-900">{loading ? '—' : activeDepts}</p>
          </div>
        </div>
        <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center gap-4">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#F0FDF4' }}>
            <CheckCircle size={18} style={{ color: '#22C55E' }} />
          </div>
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Cities Covered</p>
            <p className="text-3xl font-black text-gray-900">{loading ? '—' : cities}</p>
          </div>
        </div>
        <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center gap-4">
          <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#EFF6FF' }}>
            <Users size={18} style={{ color: '#3B82F6' }} />
          </div>
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Assigned Officers</p>
            <p className="text-3xl font-black text-gray-900">{loading ? '—' : officersSet.size}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <div className="px-6 py-4 border-b border-warm-border">
          <h2 className="text-base font-bold text-gray-900">Routing Table</h2>
          <p className="text-xs text-gray-400 mt-0.5">Live complaint auto-routing configuration</p>
        </div>
        {loading ? (
          <div className="px-6 py-4 flex flex-col gap-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-12 bg-gray-100 animate-pulse rounded-2xl" />
            ))}
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-50">
                {['City', 'Department', 'Full Name', 'Officer', 'Notification Email', 'Status'].map(h => (
                  <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-6 py-3">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr><td colSpan={6} className="px-6 py-8 text-center text-sm text-gray-400">No routing entries found.</td></tr>
              ) : rows.map((row) => (
                <tr key={row.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-semibold text-gray-800 capitalize">{row.city}</td>
                  <td className="px-6 py-4">
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}>
                      {row.department?.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{row.department_name}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{row.officer_name || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-400">{row.officer_email || '—'}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: row.is_active ? '#22C55E' : '#9CA3AF' }} />
                      <span className="text-xs font-medium" style={{ color: row.is_active ? '#22C55E' : '#9CA3AF' }}>
                        {row.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
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

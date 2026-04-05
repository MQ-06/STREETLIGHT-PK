import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2 } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch } from '../../utils/auth'
import { DEPT_LABEL } from '../../utils/theme'

export default function CityAdminDepartments() {
  const navigate = useNavigate()
  const [rows,    setRows]    = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    authFetch('/admin/routing')
      .then(r => r.json())
      .then(d => { setRows(d.routing || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const cityLabel = rows[0]?.city
    ? rows[0].city.charAt(0).toUpperCase() + rows[0].city.slice(1)
    : 'City'

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title={cityLabel + ' Departments'} subtitle="Department routing and officer assignments for your city.">
        <button onClick={() => navigate('/complaint-management')} className="px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600">
          All Complaints
        </button>
      </PageHeader>

      {loading ? (
        <div className="grid grid-cols-2 gap-4">
          {[1, 2].map(i => <div key={i} className="h-40 bg-gray-100 animate-pulse rounded-3xl" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {rows.map((row) => (
            <div key={row.id} className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#FFF3EB' }}>
                  <Building2 size={18} style={{ color: '#B85C2E' }} />
                </div>
                <div>
                  <p className="font-black text-gray-900 uppercase">{row.department}</p>
                  <p className="text-xs text-gray-400">{DEPT_LABEL[row.department] || row.department_name}</p>
                </div>
              </div>
              {row.officer_name && (
                <p className="text-xs text-gray-500 mb-1">
                  Officer: <span className="font-semibold text-gray-700">{row.officer_name}</span>
                </p>
              )}
              {row.officer_email && (
                <p className="text-xs text-gray-400 mb-3 truncate">{row.officer_email}</p>
              )}
              <div className="flex items-center gap-1.5 mb-3">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: row.is_active ? '#22C55E' : '#9CA3AF' }} />
                <span className="text-xs font-medium" style={{ color: row.is_active ? '#22C55E' : '#9CA3AF' }}>
                  {row.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <button
                onClick={() => navigate('/complaint-management')}
                className="w-full py-2 rounded-xl text-xs font-bold text-primary border border-warm-border hover:bg-gray-50"
              >
                View Complaints
              </button>
            </div>
          ))}
          {rows.length === 0 && (
            <div className="col-span-2 py-12 text-center text-sm text-gray-400">No departments found.</div>
          )}
        </div>
      )}
    </div>
  )
}

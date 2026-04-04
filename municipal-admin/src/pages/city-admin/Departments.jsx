import { useNavigate } from 'react-router-dom'
import { Building2, Users, Settings } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import EmptyState from '../../components/EmptyState'
import { getCity } from '../../utils/auth'
import { DEPT_LABEL } from '../../utils/theme'

const CITY_DEPTS = {
  lahore:     [{ dept: 'lmc',  issueTypes: ['road', 'pothole', 'infrastructure'] }, { dept: 'lwmc', issueTypes: ['garbage', 'trash', 'waste'] }],
  faisalabad: [{ dept: 'fmc',  issueTypes: ['road', 'pothole', 'infrastructure'] }, { dept: 'fwmc', issueTypes: ['garbage', 'trash', 'waste'] }],
}

export default function CityAdminDepartments() {
  const navigate = useNavigate()
  const city = getCity()
  const cityLabel = city ? city.charAt(0).toUpperCase() + city.slice(1) : 'City'
  const depts = CITY_DEPTS[city?.toLowerCase()] || []

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title={cityLabel + ' Departments'} subtitle="Department routing and officer assignments for your city.">
        <button onClick={() => navigate('/complaint-management')} className="px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600">All Complaints</button>
      </PageHeader>

      <div className="grid grid-cols-2 gap-4">
        {depts.map(({ dept }) => (
          <div key={dept} className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-11 h-11 rounded-2xl flex items-center justify-center" style={{ backgroundColor: '#FFF3EB' }}>
                <Building2 size={18} style={{ color: '#B85C2E' }} />
              </div>
              <div>
                <p className="font-black text-gray-900 uppercase">{dept}</p>
                <p className="text-xs text-gray-400">{DEPT_LABEL[dept] || dept}</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 mb-3">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              <span className="text-xs font-medium text-green-600">Active</span>
            </div>
            <button
              onClick={() => navigate('/complaint-management')}
              className="w-full py-2 rounded-xl text-xs font-bold text-primary border border-warm-border hover:bg-gray-50"
            >
              View Complaints
            </button>
          </div>
        ))}
      </div>

      <EmptyState icon={<Settings size={32} />} title="Department Management Coming Soon" description="Edit issue type mappings and officer assignments from this panel." phase={3} />
    </div>
  )
}

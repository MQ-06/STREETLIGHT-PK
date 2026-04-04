import { getRole } from '../utils/auth'
import DeptOfficerDashboard from './dept-officer/Dashboard'
import CityAdminDashboard   from './city-admin/Dashboard'
import SuperAdminDashboard  from './super-admin/Dashboard'

export default function Dashboard() {
  const role = getRole()
  if (role === 'dept_officer') return <DeptOfficerDashboard />
  if (role === 'city_admin')   return <CityAdminDashboard />
  return <SuperAdminDashboard />
}

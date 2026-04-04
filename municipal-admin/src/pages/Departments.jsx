import { getRole } from '../utils/auth'
import CityAdminDepartments from './city-admin/Departments'
import SuperAdminDepartments from './super-admin/Departments'

export default function Departments() {
  const role = getRole()
  if (role === 'city_admin') return <CityAdminDepartments />
  return <SuperAdminDepartments />
}

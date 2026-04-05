import { getRole } from '../utils/auth'
import SuperAdminUserRoles from './super-admin/UserRoles'
import CityAdminUserRoles  from './city-admin/UserRoles'

export default function UserRoles() {
  const role = getRole()
  if (role === 'city_admin') return <CityAdminUserRoles />
  return <SuperAdminUserRoles />
}

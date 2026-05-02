import { useSearchParams } from 'react-router-dom'
import { Building2, Users } from 'lucide-react'
import { getRole } from '../utils/auth'
import SuperAdminDepartments from './super-admin/Departments'
import SuperAdminUserRoles from './super-admin/UserRoles'
import CityAdminDepartments from './city-admin/Departments'
import CityAdminUserRoles from './city-admin/UserRoles'

const VALID_TABS = new Set(['departments', 'users'])

export default function Organization() {
  const role = getRole()
  const [searchParams, setSearchParams] = useSearchParams()
  const raw = searchParams.get('tab') || 'departments'
  const tab = VALID_TABS.has(raw) ? raw : 'departments'

  function setTab(next) {
    if (next === 'departments') {
      setSearchParams({}, { replace: true })
    } else {
      setSearchParams({ tab: next }, { replace: true })
    }
  }

  const DepComponent = role === 'city_admin' ? CityAdminDepartments : SuperAdminDepartments
  const UsersComponent = role === 'city_admin' ? CityAdminUserRoles : SuperAdminUserRoles

  const tabBase =
    'flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold transition-all'
  const tabActive = 'bg-primary text-white shadow-sm'
  const tabIdle = 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'

  return (
    <div className="flex min-h-full flex-col gap-5 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-gray-900">Organization</h1>
          <p className="mt-0.5 text-sm text-gray-400">
            {role === 'city_admin'
              ? 'Department routing and officers in your city'
              : 'Municipal routing, departments, and admin accounts nationwide'}
          </p>
        </div>

        <div
          className="flex w-full gap-1 rounded-2xl border border-warm-border bg-white p-1 shadow-sm sm:w-auto"
          role="tablist"
        >
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'departments'}
            onClick={() => setTab('departments')}
            className={`${tabBase} flex-1 sm:flex-initial ${tab === 'departments' ? tabActive : tabIdle}`}
          >
            <Building2 size={15} strokeWidth={2.2} />
            Departments
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'users'}
            onClick={() => setTab('users')}
            className={`${tabBase} flex-1 sm:flex-initial ${tab === 'users' ? tabActive : tabIdle}`}
          >
            <Users size={15} strokeWidth={2.2} />
            User roles
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1">
        {tab === 'departments' ? (
          <DepComponent embedded />
        ) : (
          <UsersComponent embedded />
        )}
      </div>
    </div>
  )
}

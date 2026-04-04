import { useNavigate, useLocation } from 'react-router-dom'
import {
  BarChart2, ClipboardList, Map, FileText,
  Users, Eye, LogOut, Layers, Building2, ShieldCheck,
} from 'lucide-react'
import { clearAuthData, getCurrentUser, getRole } from '../utils/auth'
import { ROLE_LABEL, DEPT_LABEL } from '../utils/theme'

const NAV = [
  { label: 'Overview',          icon: BarChart2,    path: '/dashboard',             roles: null },
  { label: 'All Complaints',    icon: ClipboardList,path: '/complaint-management',  roles: null },
  { label: 'Resolution Board',  icon: Layers,       path: '/resolution-board',      roles: null },
  { label: 'Live Map',          icon: Map,          path: '/hotspot-map',           roles: null },
  { label: 'Analytics',         icon: FileText,     path: '/analytics',             roles: null },
  { label: 'Departments',       icon: Building2,    path: '/departments',           roles: ['super_admin', 'city_admin'] },
  { label: 'User Roles',        icon: Users,        path: '/user-roles',            roles: ['super_admin'] },
  { label: 'Transparency',      icon: Eye,          path: '/transparency',          roles: ['super_admin', 'city_admin'] },
]

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const role     = getRole()
  const user     = getCurrentUser()

  const links = NAV.filter(({ roles }) => !roles || roles.includes(role))

  function handleLogout() {
    clearAuthData()
    navigate('/signin', { replace: true })
  }

  const roleLabel = ROLE_LABEL[role] || 'Admin'
  const initials  = user
    ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}`.toUpperCase()
    : 'A'
  const deptDisplay = user?.department ? DEPT_LABEL[user.department] || user.department.toUpperCase() : null
  const cityDisplay = user?.city ? user.city.charAt(0).toUpperCase() + user.city.slice(1) : null

  return (
    <aside
      className="w-64 shrink-0 flex flex-col h-full"
      style={{ backgroundColor: '#F7F6E8', borderRight: '1px solid #EDE8DC' }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-2.5 px-6 py-5 cursor-pointer shrink-0"
        onClick={() => navigate('/dashboard')}
      >
        <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-primary shadow-sm shadow-primary/30">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#fff" />
            <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#fff" />
            <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#fff" />
            <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#fff" />
          </svg>
        </div>
        <div>
          <span className="font-black text-base tracking-tight text-primary">Streetlight</span>
          <p className="text-xs text-gray-400 -mt-0.5">Admin Portal</p>
        </div>
      </div>

      {/* Role pill */}
      <div className="px-5 mb-2">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl w-fit" style={{ backgroundColor: '#FFF3EB' }}>
          <ShieldCheck size={12} className="text-primary" />
          <span className="text-xs font-bold text-primary">{roleLabel}</span>
          {cityDisplay && <span className="text-xs text-gray-400">· {cityDisplay}</span>}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 flex flex-col gap-0.5 mt-1 overflow-y-auto">
        {links.map(({ label, icon: Icon, path }) => {
          const active = location.pathname === path || location.pathname.startsWith(path + '/')
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all w-full text-left"
              style={{
                backgroundColor: active ? '#B85C2E' : 'transparent',
                color:           active ? '#fff'    : '#6B7280',
              }}
            >
              <Icon size={15} />
              {label}
            </button>
          )
        })}
      </nav>

      {/* User + Logout */}
      <div className="px-4 py-4 shrink-0" style={{ borderTop: '1px solid #EDE8DC' }}>
        <div className="flex items-center gap-3 mb-3">
          <div
            className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-black text-white shrink-0 shadow-sm"
            style={{ backgroundColor: '#B85C2E' }}
          >
            {initials}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-bold text-gray-800 truncate leading-tight">
              {user ? `${user.first_name} ${user.last_name}` : 'Admin'}
            </p>
            <p className="text-xs text-gray-400 truncate leading-tight mt-0.5">
              {deptDisplay || cityDisplay || roleLabel}
            </p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 rounded-xl text-sm font-semibold text-gray-500 hover:bg-white hover:text-gray-700 transition-colors"
        >
          <LogOut size={14} />
          Sign Out
        </button>
      </div>
    </aside>
  )
}

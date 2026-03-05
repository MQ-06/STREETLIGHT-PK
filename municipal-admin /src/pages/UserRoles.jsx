import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Search, ChevronDown, SlidersHorizontal, Shield, Pencil, UserPlus } from 'lucide-react'

const NAV_LINKS = [
  { label: 'DASHBOARD',     path: '/dashboard' },
  { label: 'COMPLAINTS',    path: '/complaint-management' },
  { label: 'USERS & ROLES', path: '/user-roles' },
  { label: 'REPORTS',       path: '/analytics' },
]

const ROLE_STATS = [
  { label: 'ADMINS',         value: '04', icon: '🛡', iconBg: '#fff0e6', filter: 'Admin' },
  { label: 'SUPERVISORS',    value: '12', icon: '👥', iconBg: '#fff0e6', filter: 'Supervisor' },
  { label: 'FIELD OFFICERS', value: '86', icon: '👤', iconBg: '#fff0e6', filter: 'Field Officer' },
]

const ROLE_BADGE = {
  ADMIN:           { bg: '#fce8e8', color: '#e05555' },
  SUPERVISOR:      { bg: '#e8f0fe', color: '#3b6ef0' },
  'FIELD OFFICER': { bg: '#fef3e2', color: '#d4860b' },
}

const USERS = [
  {
    name: 'Michael Chen',
    id: 'ID: #OFF-2024-001',
    role: 'ADMIN',
    email: 'm.chen@city.gov',
    phone: '+65 9123 4567',
    status: 'Active',
    avatar: 'https://i.pravatar.cc/40?img=11',
    initials: null,
  },
  {
    name: 'Sarah Williams',
    id: 'ID: #OFF-2024-042',
    role: 'SUPERVISOR',
    email: 's.williams@city.gov',
    phone: '+65 9876 5432',
    status: 'Active',
    avatar: 'https://i.pravatar.cc/40?img=5',
    initials: null,
  },
  {
    name: 'Robert Junior',
    id: 'ID: #OFF-2024-089',
    role: 'FIELD OFFICER',
    email: 'r.junior@city.gov',
    phone: '+65 9111 2222',
    status: 'Inactive',
    avatar: null,
    initials: 'RJ',
  },
]

export default function UserRoles() {
  const navigate = useNavigate()
  const location = useLocation()
  const [search, setSearch]       = useState('')
  const [roleFilter, setRoleFilter] = useState('All Roles')

  const filtered = USERS.filter(u => {
    const matchSearch = u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      u.role.toLowerCase().includes(search.toLowerCase())
    const matchRole = roleFilter === 'All Roles' || u.role === roleFilter.toUpperCase()
    return matchSearch && matchRole
  })

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-8 bg-white border-b border-gray-100 shrink-0">
        {/* Logo → dashboard */}
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => navigate('/dashboard')}
        >
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#b85c2a' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#fff" />
              <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#fff" />
              <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#fff" />
              <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#fff" />
            </svg>
          </div>
          <span className="font-extrabold text-sm tracking-widest uppercase" style={{ color: '#b85c2a' }}>
            Streetlight
          </span>
        </div>

        {/* Nav */}
        <nav className="flex items-center gap-8">
          <button className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center text-sm mr-2">
            🌙
          </button>
          {NAV_LINKS.map(({ label, path }) => (
            <button
              key={label}
              onClick={() => navigate(path)}
              className="text-xs font-bold tracking-widest pb-1 transition-colors"
              style={{
                color: location.pathname === path ? '#b85c2a' : '#6b7280',
                borderBottom: location.pathname === path ? '2px solid #b85c2a' : '2px solid transparent',
              }}
            >
              {label}
            </button>
          ))}
        </nav>

        {/* Right — avatar stays on same page */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-bold text-gray-800 leading-tight">Admin Panel</p>
            <p className="text-xs text-gray-400">Alex Johnson</p>
          </div>
          <img
            src="https://i.pravatar.cc/36?img=1"
            alt="admin"
            className="w-9 h-9 rounded-full object-cover"
          />
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="flex-1 overflow-y-auto px-8 py-7 flex flex-col gap-6">

        {/* Page header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">User & Role Management</h1>
            <p className="text-sm text-gray-500 mt-1">Control access levels and manage municipal officer accounts.</p>
          </div>
          {/* Add New User — stays on page, just resets filter */}
          <button
            onClick={() => setRoleFilter('All Roles')}
            className="flex items-center gap-2 px-5 py-3 rounded-xl text-white text-sm font-semibold shadow-sm"
            style={{ backgroundColor: '#b85c2a' }}
          >
            <UserPlus size={15} /> Add New User
          </button>
        </div>

        {/* ── ROLE STAT CARDS — click to filter ── */}
        <div className="grid grid-cols-3 gap-4">
          {ROLE_STATS.map((s) => (
            <div
              key={s.label}
              className="bg-white rounded-2xl px-6 py-5 shadow-sm flex items-center gap-4 cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => setRoleFilter(s.filter)}
            >
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-xl shrink-0"
                style={{ backgroundColor: s.iconBg }}
              >
                {s.icon}
              </div>
              <div>
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-1">{s.label}</p>
                <p className="text-3xl font-extrabold text-gray-900">{s.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ── USER TABLE CARD ── */}
        <div className="bg-white rounded-2xl shadow-sm flex flex-col overflow-hidden">

          {/* Search + filter bar */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
            <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5 w-80">
              <Search size={14} className="text-gray-400 shrink-0" />
              <input
                type="text"
                placeholder="Search by name, email or role..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="flex-1 bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none"
              />
            </div>
            <div className="flex items-center gap-2">
              <div className="relative flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5">
                <select
                  value={roleFilter}
                  onChange={e => setRoleFilter(e.target.value)}
                  className="bg-transparent text-sm text-gray-600 outline-none appearance-none cursor-pointer pr-5"
                >
                  <option>All Roles</option>
                  <option>Admin</option>
                  <option>Supervisor</option>
                  <option>Field Officer</option>
                </select>
                <ChevronDown size={13} className="text-gray-400 absolute right-3 pointer-events-none" />
              </div>
              <button className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200">
                <SlidersHorizontal size={15} />
              </button>
            </div>
          </div>

          {/* Table header */}
          <div className="grid grid-cols-5 gap-4 px-6 py-3 border-b border-gray-100">
            {['OFFICER NAME', 'ROLE', 'CONTACT INFO', 'STATUS', 'ACTIONS'].map(h => (
              <p key={h} className="text-xs font-bold tracking-widest text-gray-400">{h}</p>
            ))}
          </div>

          {/* Table rows — click row → complaint-management (officer's assigned complaints) */}
          <div className="flex flex-col divide-y divide-gray-50">
            {filtered.map((u, i) => (
              <div
                key={i}
                className="grid grid-cols-5 gap-4 items-center px-6 py-4 hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => navigate('/complaint-management')}
              >
                {/* Name */}
                <div className="flex items-center gap-3">
                  {u.avatar ? (
                    <img src={u.avatar} alt={u.name} className="w-10 h-10 rounded-full object-cover shrink-0" />
                  ) : (
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                      style={{ backgroundColor: '#e5e7eb', color: '#6b7280' }}
                    >
                      {u.initials}
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-bold text-gray-900">{u.name}</p>
                    <p className="text-xs text-gray-400">{u.id}</p>
                  </div>
                </div>

                {/* Role badge */}
                <div>
                  <span
                    className="text-xs font-bold px-3 py-1.5 rounded-full tracking-wide"
                    style={{
                      backgroundColor: ROLE_BADGE[u.role]?.bg || '#f3f4f6',
                      color: ROLE_BADGE[u.role]?.color || '#6b7280',
                    }}
                  >
                    {u.role}
                  </span>
                </div>

                {/* Contact */}
                <div>
                  <p className="text-sm text-gray-700">{u.email}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{u.phone}</p>
                </div>

                {/* Status */}
                <div className="flex items-center gap-2">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: u.status === 'Active' ? '#22c55e' : '#9ca3af' }}
                  />
                  <span
                    className="text-sm font-medium"
                    style={{ color: u.status === 'Active' ? '#22c55e' : '#9ca3af' }}
                  >
                    {u.status}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                  {/* Shield → departments */}
                  <button
                    className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-gray-100"
                    style={{ color: u.status === 'Active' ? '#6b7280' : '#d1d5db' }}
                    onClick={e => { e.stopPropagation(); navigate('/departments') }}
                  >
                    <Shield size={15} />
                  </button>
                  {/* Pencil → resolution-board */}
                  <button
                    className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:bg-gray-100"
                    style={{ color: u.status === 'Active' ? '#6b7280' : '#d1d5db' }}
                    onClick={e => { e.stopPropagation(); navigate('/resolution-board') }}
                  >
                    <Pencil size={15} />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100">
            <p className="text-sm text-gray-500">
              Showing <span className="font-bold text-gray-800">1 to 10</span> of{' '}
              <span className="font-bold text-gray-800">102</span> users
            </p>
            <div className="flex items-center gap-2">
              <button className="px-4 py-2 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors">
                Previous
              </button>
              <button
                className="px-4 py-2 rounded-xl text-sm font-semibold text-white transition-colors"
                style={{ backgroundColor: '#b85c2a' }}
              >
                Next
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-400 py-2">
          © 2024 Streetlight Civic-Tech Solutions. All rights reserved.
        </p>

      </div>
    </div>
  )
}
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, ChevronDown, SlidersHorizontal, Shield, Pencil, UserPlus } from 'lucide-react'
import PageHeader from '../../components/PageHeader'

const ROLE_STATS = [
  { label: 'Super Admins',   value: '1',  icon: '🛡', iconBg: '#FFF3EB', filter: 'super_admin'  },
  { label: 'City Admins',    value: '2',  icon: '🏙', iconBg: '#EFF6FF', filter: 'city_admin'   },
  { label: 'Dept. Officers', value: '4',  icon: '👤', iconBg: '#F0FDF4', filter: 'dept_officer' },
]

const ROLE_BADGE = {
  super_admin:  { bg: '#FEF2F2', color: '#E05555', label: 'Super Admin'  },
  city_admin:   { bg: '#EFF6FF', color: '#3B6EF0', label: 'City Admin'   },
  dept_officer: { bg: '#FEF3E2', color: '#D4860B', label: 'Dept. Officer'},
}

const SEED_USERS = [
  { name: 'Super Admin', email: 'super@streetlight.local', role: 'super_admin', city: null,        dept: null,   status: 'Active' },
  { name: 'Lahore Admin', email: 'lahore@streetlight.local', role: 'city_admin', city: 'Lahore',   dept: null,   status: 'Active' },
  { name: 'FSD Admin',    email: 'fsd@streetlight.local',    role: 'city_admin', city: 'Faisalabad', dept: null, status: 'Active' },
  { name: 'LMC Officer',  email: 'lmc@streetlight.local',    role: 'dept_officer', city: 'Lahore', dept: 'LMC',  status: 'Active' },
  { name: 'LWMC Officer', email: 'lwmc@streetlight.local',   role: 'dept_officer', city: 'Lahore', dept: 'LWMC', status: 'Active' },
  { name: 'FMC Officer',  email: 'fmc@streetlight.local',    role: 'dept_officer', city: 'Faisalabad', dept: 'FMC', status: 'Active' },
  { name: 'FWMC Officer', email: 'fwmc@streetlight.local',   role: 'dept_officer', city: 'Faisalabad', dept: 'FWMC', status: 'Active' },
]

export default function UserRoles() {
  const navigate = useNavigate()
  const [search,     setSearch]     = useState('')
  const [roleFilter, setRoleFilter] = useState('All')

  const filtered = SEED_USERS.filter(u => {
    const matchSearch = u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
    const matchRole = roleFilter === 'All' || u.role === roleFilter
    return matchSearch && matchRole
  })

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="User & Role Management" subtitle="Control access levels and manage municipal officer accounts.">
        <button
          onClick={() => setRoleFilter('All')}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark transition-colors"
        >
          <UserPlus size={15} /> Add New User
        </button>
      </PageHeader>

      <div className="grid grid-cols-3 gap-4">
        {ROLE_STATS.map(s => (
          <div
            key={s.label}
            className="bg-white rounded-3xl px-6 py-5 shadow-sm border border-warm-border flex items-center gap-4 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => setRoleFilter(s.filter)}
          >
            <div className="w-12 h-12 rounded-full flex items-center justify-center text-xl shrink-0" style={{ backgroundColor: s.iconBg }}>
              {s.icon}
            </div>
            <div>
              <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-1">{s.label}</p>
              <p className="text-3xl font-black text-gray-900">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-warm-border">
          <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5 w-80">
            <Search size={14} className="text-gray-400 shrink-0" />
            <input
              type="text"
              placeholder="Search by name or email..."
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
                <option value="All">All Roles</option>
                <option value="super_admin">Super Admin</option>
                <option value="city_admin">City Admin</option>
                <option value="dept_officer">Dept. Officer</option>
              </select>
              <ChevronDown size={13} className="text-gray-400 absolute right-3 pointer-events-none" />
            </div>
            <button className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center text-gray-500">
              <SlidersHorizontal size={15} />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4 px-6 py-3 border-b border-warm-border">
          {['OFFICER NAME', 'ROLE', 'CITY / DEPT', 'STATUS', 'ACTIONS'].map(h => (
            <p key={h} className="text-xs font-bold tracking-widest text-gray-400">{h}</p>
          ))}
        </div>

        <div className="flex flex-col divide-y divide-gray-50">
          {filtered.map((u, i) => {
            const badge = ROLE_BADGE[u.role] || { bg: '#F3F4F6', color: '#6B7280', label: u.role }
            const initials = u.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
            return (
              <div
                key={i}
                className="grid grid-cols-5 gap-4 items-center px-6 py-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => navigate('/complaint-management')}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ backgroundColor: '#B85C2E', color: '#fff' }}
                  >
                    {initials}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">{u.name}</p>
                    <p className="text-xs text-gray-400">{u.email}</p>
                  </div>
                </div>
                <div>
                  <span className="text-xs font-bold px-3 py-1.5 rounded-full" style={{ backgroundColor: badge.bg, color: badge.color }}>
                    {badge.label}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  {u.city && <p>{u.city}</p>}
                  {u.dept && <p className="text-xs text-gray-400 uppercase">{u.dept}</p>}
                  {!u.city && !u.dept && <p className="text-gray-400">—</p>}
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: u.status === 'Active' ? '#22C55E' : '#9CA3AF' }} />
                  <span className="text-sm font-medium" style={{ color: u.status === 'Active' ? '#22C55E' : '#9CA3AF' }}>
                    {u.status}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-gray-500"
                    onClick={e => { e.stopPropagation(); navigate('/departments') }}
                  >
                    <Shield size={15} />
                  </button>
                  <button
                    className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-gray-500"
                    onClick={e => { e.stopPropagation(); navigate('/resolution-board') }}
                  >
                    <Pencil size={15} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex items-center justify-between px-6 py-4 border-t border-warm-border">
          <p className="text-sm text-gray-500">
            Showing <span className="font-bold text-gray-800">{filtered.length}</span> of{' '}
            <span className="font-bold text-gray-800">{SEED_USERS.length}</span> users
          </p>
        </div>
      </div>
    </div>
  )
}

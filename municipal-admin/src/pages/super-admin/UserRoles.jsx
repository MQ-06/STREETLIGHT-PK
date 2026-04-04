import { useState, useEffect } from 'react'
import { Search, ChevronDown, SlidersHorizontal, Shield, Pencil, UserPlus, X } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch } from '../../utils/auth'

const ROLE_BADGE = {
  super_admin:  { bg: '#FEF2F2', color: '#E05555', label: 'Super Admin'   },
  city_admin:   { bg: '#EFF6FF', color: '#3B6EF0', label: 'City Admin'    },
  dept_officer: { bg: '#FEF3E2', color: '#D4860B', label: 'Dept. Officer' },
}

const CITY_DEPTS = {
  lahore:      ['lmc', 'lwmc'],
  faisalabad:  ['fmc', 'fwmc'],
}

const EMPTY_FORM = {
  first_name: '', last_name: '', email: '', password: '',
  role: 'dept_officer', city: 'lahore', department: 'lmc',
  notification_email: '',
}

export default function UserRoles() {
  const [users,      setUsers]      = useState([])
  const [loading,    setLoading]    = useState(true)
  const [search,     setSearch]     = useState('')
  const [roleFilter, setRoleFilter] = useState('All')
  const [showModal,  setShowModal]  = useState(false)
  const [form,       setForm]       = useState(EMPTY_FORM)
  const [saving,     setSaving]     = useState(false)
  const [formError,  setFormError]  = useState('')

  // Edit modal state
  const [editUser,    setEditUser]    = useState(null)
  const [editForm,    setEditForm]    = useState({})
  const [editSaving,  setEditSaving]  = useState(false)
  const [editError,   setEditError]   = useState('')

  function loadUsers() {
    setLoading(true)
    authFetch('/admin/users')
      .then(r => r.json())
      .then(d => { setUsers(Array.isArray(d) ? d : (d.users || [])); setLoading(false) })
      .catch(() => setLoading(false))
  }

  useEffect(() => { loadUsers() }, [])

  const roleCounts = users.reduce((acc, u) => {
    acc[u.role] = (acc[u.role] || 0) + 1
    return acc
  }, {})

  const ROLE_STATS = [
    { label: 'Super Admins',   value: roleCounts.super_admin  || 0, icon: '🛡', iconBg: '#FFF3EB', filter: 'super_admin'  },
    { label: 'City Admins',    value: roleCounts.city_admin   || 0, icon: '🏙', iconBg: '#EFF6FF', filter: 'city_admin'   },
    { label: 'Dept. Officers', value: roleCounts.dept_officer || 0, icon: '👤', iconBg: '#F0FDF4', filter: 'dept_officer' },
  ]

  const filtered = users.filter(u => {
    const name  = ((u.first_name || '') + ' ' + (u.last_name || '')).toLowerCase()
    const email = (u.email || '').toLowerCase()
    const term  = search.toLowerCase()
    const matchSearch = name.includes(term) || email.includes(term)
    const matchRole   = roleFilter === 'All' || u.role === roleFilter
    return matchSearch && matchRole
  })

  function openEdit(u) {
    setEditUser(u)
    setEditError('')
    setEditForm({
      notification_email: u.notification_email || '',
      city:               u.city               || '',
      department:         u.department          || '',
      is_active:          u.is_active !== false,
    })
  }

  async function handleEditSave(e) {
    e.preventDefault()
    setEditError('')
    setEditSaving(true)
    const body = {}
    if (editForm.notification_email !== (editUser.notification_email || '')) body.notification_email = editForm.notification_email
    if (editForm.city        !== (editUser.city       || '')) body.city        = editForm.city
    if (editForm.department  !== (editUser.department || '')) body.department  = editForm.department
    if (editForm.is_active   !== (editUser.is_active !== false)) body.is_active = editForm.is_active
    try {
      const res = await authFetch('/admin/users/' + editUser.id, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setEditError(err.detail || 'Failed to update user.')
        setEditSaving(false)
        return
      }
      setEditUser(null)
      loadUsers()
    } catch {
      setEditError('Network error.')
    }
    setEditSaving(false)
  }

  async function handleCreateUser(e) {
    e.preventDefault()
    setFormError('')
    if (!form.first_name || !form.last_name || !form.email || !form.password) {
      setFormError('All fields are required.')
      return
    }
    setSaving(true)
    const body = {
      first_name: form.first_name,
      last_name:  form.last_name,
      email:      form.email,
      password:   form.password,
      role:       form.role,
    }
    if (form.role === 'city_admin' || form.role === 'dept_officer') body.city = form.city
    if (form.role === 'dept_officer') body.department = form.department
    if (form.notification_email) body.notification_email = form.notification_email

    try {
      const res = await authFetch('/admin/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setFormError(err.detail || 'Failed to create user.')
        setSaving(false)
        return
      }
      setShowModal(false)
      setForm(EMPTY_FORM)
      loadUsers()
    } catch {
      setFormError('Network error. Please try again.')
    }
    setSaving(false)
  }

  const depts = CITY_DEPTS[form.city] || []

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="User & Role Management" subtitle="Control access levels and manage municipal officer accounts.">
        <button
          onClick={() => { setShowModal(true); setFormError('') }}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark transition-colors"
        >
          <UserPlus size={15} /> Add New User
        </button>
      </PageHeader>

      {/* Role Stats */}
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
              <p className="text-3xl font-black text-gray-900">{loading ? '…' : s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* User Table */}
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
          {loading ? (
            <div className="py-12 text-center text-sm text-gray-400">Loading users…</div>
          ) : filtered.length === 0 ? (
            <div className="py-12 text-center text-sm text-gray-400">No users found.</div>
          ) : filtered.map((u, i) => {
            const badge    = ROLE_BADGE[u.role] || { bg: '#F3F4F6', color: '#6B7280', label: u.role }
            const fullName = ((u.first_name || '') + ' ' + (u.last_name || '')).trim() || u.email
            const initials = fullName.split(' ').filter(Boolean).map(n => n[0]).join('').toUpperCase().slice(0, 2)
            const isActive = u.is_active !== false
            const city     = u.city       || null
            const dept     = u.department || null
            return (
              <div
                key={u.id || i}
                className="grid grid-cols-5 gap-4 items-center px-6 py-4 hover:bg-gray-50"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ backgroundColor: '#B85C2E', color: '#fff' }}
                  >
                    {initials}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">{fullName}</p>
                    <p className="text-xs text-gray-400">{u.email}</p>
                  </div>
                </div>
                <div>
                  <span className="text-xs font-bold px-3 py-1.5 rounded-full" style={{ backgroundColor: badge.bg, color: badge.color }}>
                    {badge.label}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  {city && <p className="capitalize">{city}</p>}
                  {dept && <p className="text-xs text-gray-400 uppercase">{dept}</p>}
                  {!city && !dept && <p className="text-gray-400">—</p>}
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: isActive ? '#22C55E' : '#9CA3AF' }} />
                  <span className="text-sm font-medium" style={{ color: isActive ? '#22C55E' : '#9CA3AF' }}>
                    {isActive ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-gray-500">
                    <Shield size={15} />
                  </button>
                  <button
                    className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-gray-500"
                    onClick={e => { e.stopPropagation(); openEdit(u) }}
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
            <span className="font-bold text-gray-800">{users.length}</span> users
          </p>
        </div>
      </div>

      {/* Edit User Modal */}
      {editUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-5 border-b border-warm-border">
              <div>
                <h2 className="text-lg font-black text-gray-900">Edit User</h2>
                <p className="text-xs text-gray-400 mt-0.5">{editUser.email}</p>
              </div>
              <button onClick={() => setEditUser(null)} className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200">
                <X size={15} />
              </button>
            </div>
            <form onSubmit={handleEditSave} className="p-6 flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Notification Email</label>
                <input type="email" value={editForm.notification_email}
                  onChange={e => setEditForm(f => ({ ...f, notification_email: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="officer@gmail.com" />
              </div>

              {(editUser.role === 'city_admin' || editUser.role === 'dept_officer') && (
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">City</label>
                  <select value={editForm.city}
                    onChange={e => setEditForm(f => ({ ...f, city: e.target.value, department: CITY_DEPTS[e.target.value]?.[0] || '' }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white">
                    <option value="lahore">Lahore</option>
                    <option value="faisalabad">Faisalabad</option>
                  </select>
                </div>
              )}

              {editUser.role === 'dept_officer' && (
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">Department</label>
                  <select value={editForm.department}
                    onChange={e => setEditForm(f => ({ ...f, department: e.target.value }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white">
                    {(CITY_DEPTS[editForm.city] || []).map(d => (
                      <option key={d} value={d}>{d.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex items-center justify-between p-3 rounded-xl border border-warm-border">
                <div>
                  <p className="text-sm font-semibold text-gray-800">Account Active</p>
                  <p className="text-xs text-gray-400">Inactive users cannot log in</p>
                </div>
                <button type="button"
                  onClick={() => setEditForm(f => ({ ...f, is_active: !f.is_active }))}
                  className="relative w-11 h-6 rounded-full transition-colors"
                  style={{ backgroundColor: editForm.is_active ? '#22C55E' : '#D1D5DB' }}>
                  <span className="absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-all"
                        style={{ left: editForm.is_active ? '22px' : '2px' }} />
                </button>
              </div>

              {editError && <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded-xl">{editError}</p>}

              <div className="flex gap-3 mt-1">
                <button type="button" onClick={() => setEditUser(null)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50">
                  Cancel
                </button>
                <button type="submit" disabled={editSaving}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-60">
                  {editSaving ? 'Saving…' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-5 border-b border-warm-border">
              <h2 className="text-lg font-black text-gray-900">Add New User</h2>
              <button onClick={() => setShowModal(false)} className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200">
                <X size={15} />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="p-6 flex flex-col gap-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">First Name</label>
                  <input
                    type="text" required
                    value={form.first_name}
                    onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="Ali"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">Last Name</label>
                  <input
                    type="text" required
                    value={form.last_name}
                    onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="Hassan"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Email</label>
                <input
                  type="email" required
                  value={form.email}
                  onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="officer@streetlight.local"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Password</label>
                <input
                  type="password" required
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="••••••••"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">
                  Notification Email <span className="text-gray-400 font-normal">(real inbox for alerts)</span>
                </label>
                <input
                  type="email"
                  value={form.notification_email}
                  onChange={e => setForm(f => ({ ...f, notification_email: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="officer@gmail.com"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Role</label>
                <select
                  value={form.role}
                  onChange={e => setForm(f => ({ ...f, role: e.target.value, department: CITY_DEPTS[f.city]?.[0] || '' }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white"
                >
                  <option value="dept_officer">Dept. Officer</option>
                  <option value="city_admin">City Admin</option>
                  <option value="super_admin">Super Admin</option>
                </select>
              </div>

              {(form.role === 'city_admin' || form.role === 'dept_officer') && (
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">City</label>
                  <select
                    value={form.city}
                    onChange={e => setForm(f => ({ ...f, city: e.target.value, department: CITY_DEPTS[e.target.value]?.[0] || '' }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white"
                  >
                    <option value="lahore">Lahore</option>
                    <option value="faisalabad">Faisalabad</option>
                  </select>
                </div>
              )}

              {form.role === 'dept_officer' && (
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">Department</label>
                  <select
                    value={form.department}
                    onChange={e => setForm(f => ({ ...f, department: e.target.value }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white"
                  >
                    {depts.map(d => (
                      <option key={d} value={d}>{d.toUpperCase()}</option>
                    ))}
                  </select>
                </div>
              )}

              {formError && (
                <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded-xl">{formError}</p>
              )}

              <div className="flex gap-3 mt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-60"
                >
                  {saving ? 'Creating…' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

import { useState, useEffect } from 'react'
import { Search, UserPlus, X, Pencil, User } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch, getCurrentUser } from '../../utils/auth'

const CITY_DEPTS = {
  lahore:     ['lmc', 'lwmc'],
  faisalabad: ['fmc', 'fwmc'],
}

const EMPTY_FORM = {
  first_name: '', last_name: '', email: '', password: '',
  role: 'dept_officer', department: 'lmc', notification_email: '',
}

export default function CityAdminUserRoles() {
  const currentUser = getCurrentUser()
  const city        = currentUser?.city || 'lahore'
  const cityLabel   = city.charAt(0).toUpperCase() + city.slice(1)
  const depts       = CITY_DEPTS[city] || []

  const [users,     setUsers]     = useState([])
  const [loading,   setLoading]   = useState(true)
  const [search,    setSearch]    = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form,      setForm]      = useState({ ...EMPTY_FORM, department: depts[0] || 'lmc' })
  const [saving,    setSaving]    = useState(false)
  const [formError, setFormError] = useState('')

  const [editUser,   setEditUser]   = useState(null)
  const [editForm,   setEditForm]   = useState({})
  const [editSaving, setEditSaving] = useState(false)
  const [editError,  setEditError]  = useState('')

  function loadUsers() {
    setLoading(true)
    authFetch('/admin/users')
      .then(r => r.json())
      .then(d => { setUsers(Array.isArray(d) ? d : (d.users || [])); setLoading(false) })
      .catch(() => setLoading(false))
  }
  useEffect(() => { loadUsers() }, [])

  const filtered = users.filter(u => {
    const name  = ((u.first_name || '') + ' ' + (u.last_name || '')).toLowerCase()
    const email = (u.email || '').toLowerCase()
    return name.includes(search.toLowerCase()) || email.includes(search.toLowerCase())
  })

  async function handleCreate(e) {
    e.preventDefault()
    setFormError('')
    if (!form.first_name || !form.last_name || !form.email || !form.password) {
      setFormError('All fields are required.')
      return
    }
    setSaving(true)
    const body = {
      first_name: form.first_name, last_name: form.last_name,
      email: form.email, password: form.password,
      role: 'dept_officer', city,
      department: form.department,
    }
    if (form.notification_email) body.notification_email = form.notification_email
    try {
      const res = await authFetch('/admin/users', {
        method: 'POST',
        body:   JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setFormError(err.detail || 'Failed to create user.')
        setSaving(false)
        return
      }
      setShowModal(false)
      setForm({ ...EMPTY_FORM, department: depts[0] || 'lmc' })
      loadUsers()
    } catch {
      setFormError('Network error.')
    }
    setSaving(false)
  }

  async function handleEditSave(e) {
    e.preventDefault()
    setEditError('')
    setEditSaving(true)
    const body = {}
    if (editForm.notification_email !== (editUser.notification_email || '')) body.notification_email = editForm.notification_email
    if (editForm.department !== (editUser.department || '')) body.department = editForm.department
    try {
      const res = await authFetch('/admin/users/' + editUser.id, {
        method: 'PATCH',
        body:   JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setEditError(err.detail || 'Failed to update.')
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

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title={cityLabel + ' Officers'} subtitle={`Manage dept. officers for ${cityLabel}.`}>
        <button
          onClick={() => { setShowModal(true); setFormError('') }}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark"
        >
          <UserPlus size={15} /> Add Officer
        </button>
      </PageHeader>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <div className="flex items-center px-6 py-4 border-b border-warm-border">
          <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-4 py-2.5 w-80">
            <Search size={14} className="text-gray-400 shrink-0" />
            <input
              type="text" placeholder="Search officers…"
              value={search} onChange={e => setSearch(e.target.value)}
              className="flex-1 bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none"
            />
          </div>
        </div>

        <div className="flex flex-col divide-y divide-gray-50">
          {loading ? (
            <div className="py-12 text-center text-sm text-gray-400">Loading…</div>
          ) : filtered.length === 0 ? (
            <div className="py-12 text-center text-sm text-gray-400">No officers found.</div>
          ) : filtered.map((u, i) => {
            const fullName = ((u.first_name || '') + ' ' + (u.last_name || '')).trim()
            const initials = fullName.split(' ').filter(Boolean).map(n => n[0]).join('').toUpperCase().slice(0, 2)
            const isActive = u.is_active !== false
            return (
              <div key={u.id || i} className="grid grid-cols-4 gap-4 items-center px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shrink-0"
                    style={{ backgroundColor: '#B85C2E', color: '#fff' }}>{initials}</div>
                  <div>
                    <p className="text-sm font-bold text-gray-900">{fullName}</p>
                    <p className="text-xs text-gray-400">{u.email}</p>
                  </div>
                </div>
                <div>
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ backgroundColor: '#FEF3E2', color: '#D4860B' }}>
                    {u.department?.toUpperCase() || 'DEPT'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: isActive ? '#22C55E' : '#9CA3AF' }} />
                  <span className="text-sm font-medium" style={{ color: isActive ? '#22C55E' : '#9CA3AF' }}>
                    {isActive ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div>
                  <button
                    className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 text-gray-500"
                    onClick={() => {
                      setEditUser(u)
                      setEditError('')
                      setEditForm({ notification_email: u.notification_email || '', department: u.department || depts[0] || '' })
                    }}
                  >
                    <Pencil size={15} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
        <div className="px-6 py-4 border-t border-warm-border">
          <p className="text-sm text-gray-500">{filtered.length} officer{filtered.length !== 1 ? 's' : ''}</p>
        </div>
      </div>

      {/* Edit modal */}
      {editUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-5 border-b border-warm-border">
              <div>
                <h2 className="text-lg font-black text-gray-900">Edit Officer</h2>
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
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Department</label>
                <select value={editForm.department}
                  onChange={e => setEditForm(f => ({ ...f, department: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white">
                  {depts.map(d => <option key={d} value={d}>{d.toUpperCase()}</option>)}
                </select>
              </div>
              {editError && <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded-xl">{editError}</p>}
              <div className="flex gap-3 mt-1">
                <button type="button" onClick={() => setEditUser(null)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50">Cancel</button>
                <button type="submit" disabled={editSaving}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-60">
                  {editSaving ? 'Saving…' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-5 border-b border-warm-border">
              <h2 className="text-lg font-black text-gray-900">Add New Officer — {cityLabel}</h2>
              <button onClick={() => setShowModal(false)} className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-gray-200">
                <X size={15} />
              </button>
            </div>
            <form onSubmit={handleCreate} className="p-6 flex flex-col gap-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">First Name</label>
                  <input type="text" required value={form.first_name}
                    onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="Ali" />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs font-semibold text-gray-500">Last Name</label>
                  <input type="text" required value={form.last_name}
                    onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))}
                    className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="Hassan" />
                </div>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Login Email</label>
                <input type="email" required value={form.email}
                  onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="officer@streetlight.local" />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Password</label>
                <input type="password" required value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="••••••••" />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Notification Email <span className="text-gray-400 font-normal">(real inbox)</span></label>
                <input type="email" value={form.notification_email}
                  onChange={e => setForm(f => ({ ...f, notification_email: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  placeholder="officer@gmail.com" />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs font-semibold text-gray-500">Department</label>
                <select value={form.department}
                  onChange={e => setForm(f => ({ ...f, department: e.target.value }))}
                  className="px-3 py-2.5 rounded-xl border border-warm-border text-sm outline-none focus:ring-2 focus:ring-primary/30 bg-white">
                  {depts.map(d => <option key={d} value={d}>{d.toUpperCase()}</option>)}
                </select>
              </div>
              {formError && <p className="text-sm text-red-500 bg-red-50 px-3 py-2 rounded-xl">{formError}</p>}
              <div className="flex gap-3 mt-2">
                <button type="button" onClick={() => setShowModal(false)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50">Cancel</button>
                <button type="submit" disabled={saving}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-60">
                  {saving ? 'Creating…' : 'Create Officer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

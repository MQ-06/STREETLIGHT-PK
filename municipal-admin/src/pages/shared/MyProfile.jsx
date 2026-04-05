import { useState } from 'react'
import { Bell, Save, CheckCircle } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch, getCurrentUser, setAuthData, getToken } from '../../utils/auth'

export default function MyProfile() {
  const user = getCurrentUser()
  const [notifEmail, setNotifEmail] = useState(user?.notification_email || '')
  const [saving,     setSaving]     = useState(false)
  const [saved,      setSaved]      = useState(false)
  const [error,      setError]      = useState('')

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    setError('')
    try {
      const res = await authFetch('/admin/users/' + user.id, {
        method: 'PATCH',
        body:   JSON.stringify({ notification_email: notifEmail.trim() || null }),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        setError(d.detail || 'Failed to update.')
        setSaving(false)
        return
      }
      // Update local user cache
      const updated = { ...user, notification_email: notifEmail.trim() || null }
      setAuthData(getToken(), updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError('Network error.')
    }
    setSaving(false)
  }

  const fullName = user ? `${user.first_name} ${user.last_name}` : 'Officer'
  const initials = fullName.split(' ').filter(Boolean).map(n => n[0]).join('').toUpperCase().slice(0, 2)

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="My Profile" subtitle="Update your notification settings." />

      <div className="max-w-xl flex flex-col gap-5">
        {/* Avatar card */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border flex items-center gap-5">
          <div
            className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-black text-white shrink-0"
            style={{ backgroundColor: '#B85C2E' }}
          >
            {initials}
          </div>
          <div>
            <p className="text-lg font-black text-gray-900">{fullName}</p>
            <p className="text-sm text-gray-400">{user?.email}</p>
            <span className="mt-1 inline-block text-xs font-bold px-2.5 py-1 rounded-full" style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}>
              {user?.role?.replace('_', ' ') || 'Officer'}
            </span>
          </div>
        </div>

        {/* Notification email */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <div className="flex items-center gap-2 mb-5">
            <Bell size={16} className="text-gray-500" />
            <h2 className="text-base font-bold text-gray-900">Notification Email</h2>
          </div>
          <p className="text-sm text-gray-500 mb-5 leading-relaxed">
            When a new complaint is routed to your department, an alert is sent to this email address.
            Your login email (<span className="font-semibold">{user?.email}</span>) is separate and used only for signing in.
          </p>
          <form onSubmit={handleSave} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-gray-600 uppercase tracking-widest">Real email inbox</label>
              <input
                type="email"
                value={notifEmail}
                onChange={e => setNotifEmail(e.target.value)}
                placeholder="yourname@gmail.com"
                className="px-4 py-3 rounded-xl border border-warm-border text-sm text-gray-800 outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <button
              type="submit"
              disabled={saving}
              className="flex items-center justify-center gap-2 py-3 rounded-xl bg-primary text-white text-sm font-bold hover:bg-primary-dark disabled:opacity-60 transition-colors"
            >
              {saved
                ? <><CheckCircle size={15} /> Saved!</>
                : saving
                ? 'Saving…'
                : <><Save size={15} /> Save Changes</>}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

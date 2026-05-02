import { useState } from 'react'
import {
  Bell,
  Save,
  CheckCircle,
  Shield,
  Globe2,
  Users,
  ScrollText,
  Mail,
  Lock,
  Sparkles,
} from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch, getCurrentUser, setAuthData, getToken, getRole } from '../../utils/auth'
import { ROLE_LABEL } from '../../utils/theme'

export default function MyProfile() {
  const user = getCurrentUser()
  const role = getRole()
  const isSuperAdmin = role === 'super_admin'

  const [notifEmail, setNotifEmail] = useState(user?.notification_email || '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    setError('')
    try {
      const res = await authFetch('/admin/users/' + user.id, {
        method: 'PATCH',
        body: JSON.stringify({ notification_email: notifEmail.trim() || null }),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        setError(d.detail || 'Failed to update.')
        setSaving(false)
        return
      }
      const updated = { ...user, notification_email: notifEmail.trim() || null }
      setAuthData(getToken(), updated)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError('Network error.')
    }
    setSaving(false)
  }

  const fullName = user ? `${user.first_name} ${user.last_name}` : 'Admin'
  const initials = fullName
    .split(' ')
    .filter(Boolean)
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  const roleLabel = ROLE_LABEL[role] || (user?.role?.replace('_', ' ') ?? 'Admin')

  if (isSuperAdmin) {
    return (
      <div className="p-6 flex flex-col gap-8 pb-12">
        <PageHeader
          title="Administrator profile"
          subtitle="National oversight — your account is scoped to all cities and departments."
        />

        <div className="max-w-5xl flex flex-col gap-6">
          {/* Hero identity */}
          <div className="relative overflow-hidden rounded-[28px] border border-warm-border bg-white shadow-sm">
            <div
              className="pointer-events-none absolute inset-0 opacity-[0.55]"
              style={{
                background:
                  'radial-gradient(900px 280px at 12% -20%, rgba(184,92,46,0.14), transparent 55%), radial-gradient(600px 220px at 88% 110%, rgba(184,92,46,0.08), transparent 50%)',
              }}
            />
            <div className="relative flex flex-col gap-8 p-8 md:flex-row md:items-center md:justify-between md:p-10">
              <div className="flex items-center gap-6">
                <div className="relative shrink-0">
                  <div
                    className="flex h-[88px] w-[88px] items-center justify-center rounded-full text-2xl font-black text-white shadow-md ring-[3px] ring-[#B85C2E]/25 ring-offset-4 ring-offset-white"
                    style={{ backgroundColor: '#B85C2E' }}
                  >
                    {initials}
                  </div>
                  <span
                    className="absolute -bottom-1 -right-1 flex h-9 w-9 items-center justify-center rounded-xl border-2 border-white bg-[#FFF7ED] text-[#B85C2E] shadow-sm"
                    title="Super Admin"
                  >
                    <Shield size={18} strokeWidth={2.2} />
                  </span>
                </div>
                <div className="min-w-0 space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-2xl font-black tracking-tight text-gray-900">{fullName}</p>
                    <span className="inline-flex items-center gap-1 rounded-full bg-[#FFF3EB] px-3 py-1 text-xs font-bold uppercase tracking-wide text-[#9C4C24]">
                      <Sparkles size={12} className="opacity-80" />
                      {roleLabel}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">
                    Routing alerts go to department officers — not to this role. Use the dashboard for live visibility.
                  </p>
                </div>
              </div>

              <dl className="grid shrink-0 grid-cols-1 gap-3 sm:grid-cols-3 md:border-l md:border-warm-border md:pl-10">
                <div className="rounded-2xl bg-[#FDFCF0]/90 px-4 py-3 ring-1 ring-warm-border/80">
                  <dt className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                    <Globe2 size={12} className="text-primary" /> Scope
                  </dt>
                  <dd className="mt-1 text-sm font-bold text-gray-800">Pakistan-wide</dd>
                </div>
                <div className="rounded-2xl bg-[#FDFCF0]/90 px-4 py-3 ring-1 ring-warm-border/80">
                  <dt className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                    <Users size={12} className="text-primary" /> Users
                  </dt>
                  <dd className="mt-1 text-sm font-bold text-gray-800">All admin roles</dd>
                </div>
                <div className="rounded-2xl bg-[#FDFCF0]/90 px-4 py-3 ring-1 ring-warm-border/80">
                  <dt className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                    <ScrollText size={12} className="text-primary" /> Audit
                  </dt>
                  <dd className="mt-1 text-sm font-bold text-gray-800">Full trail access</dd>
                </div>
              </dl>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Sign-in */}
            <div className="rounded-3xl border border-warm-border bg-white p-7 shadow-sm">
              <div className="mb-5 flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gray-50 ring-1 ring-warm-border">
                  <Lock size={18} className="text-gray-600" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Sign-in identity</h2>
                  <p className="text-xs text-gray-400">Used only for authentication</p>
                </div>
              </div>
              <div className="rounded-2xl bg-[#FAFAF8] px-4 py-3.5 ring-1 ring-warm-border">
                <div className="flex items-start gap-3">
                  <Mail size={16} className="mt-0.5 shrink-0 text-gray-400" />
                  <div className="min-w-0">
                    <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Login email</p>
                    <p className="truncate font-semibold text-gray-900">{user?.email ?? '—'}</p>
                  </div>
                </div>
              </div>
              <p className="mt-4 text-xs leading-relaxed text-gray-500">
                Password resets and security policies are managed outside this screen. Contact your deployment owner if you need credential changes.
              </p>
            </div>

            {/* Optional inbox */}
            <div className="rounded-3xl border border-warm-border bg-white p-7 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#FFF3EB] ring-1 ring-[#B85C2E]/15">
                  <Bell size={18} className="text-[#B85C2E]" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-gray-900">Optional contact inbox</h2>
                  <p className="text-xs text-gray-400">Not required for Super Admin operations</p>
                </div>
              </div>
              <div className="mb-5 rounded-2xl border border-dashed border-warm-border bg-[#FFFBF7] px-4 py-3 text-xs leading-relaxed text-gray-600">
                New complaints trigger emails to the <strong className="font-semibold text-gray-800">assigned department officer</strong>, not to Super Admin.
                You may still save a personal address here for optional notices or SMTP testing — leave blank if you do not need it.
              </div>
              <form onSubmit={handleSave} className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-widest text-gray-500">
                    Secondary email (optional)
                  </label>
                  <input
                    type="email"
                    value={notifEmail}
                    onChange={(e) => setNotifEmail(e.target.value)}
                    placeholder="Leave empty — or yourname@gmail.com"
                    className="rounded-xl border border-warm-border px-4 py-3 text-sm text-gray-800 outline-none transition-shadow placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/15"
                  />
                </div>
                {error && <p className="text-sm text-red-500">{error}</p>}
                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center justify-center gap-2 rounded-xl bg-primary py-3 text-sm font-bold text-white transition-colors hover:bg-[#9C4C24] disabled:opacity-60"
                >
                  {saved ? (
                    <>
                      <CheckCircle size={15} /> Saved
                    </>
                  ) : saving ? (
                    'Saving…'
                  ) : (
                    <>
                      <Save size={15} /> Save optional inbox
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    )
  }

  /* City admin & department officer — compact classic layout */
  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="My Profile" subtitle="Update your notification settings." />

      <div className="max-w-xl flex flex-col gap-5">
        <div className="flex items-center gap-5 rounded-3xl border border-warm-border bg-white p-6 shadow-sm">
          <div
            className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full text-xl font-black text-white"
            style={{ backgroundColor: '#B85C2E' }}
          >
            {initials}
          </div>
          <div>
            <p className="text-lg font-black text-gray-900">{fullName}</p>
            <p className="text-sm text-gray-400">{user?.email}</p>
            <span
              className="mt-1 inline-block rounded-full px-2.5 py-1 text-xs font-bold"
              style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}
            >
              {roleLabel}
            </span>
          </div>
        </div>

        <div className="rounded-3xl border border-warm-border bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-2">
            <Bell size={16} className="text-gray-500" />
            <h2 className="text-base font-bold text-gray-900">Notification Email</h2>
          </div>
          <p className="mb-5 text-sm leading-relaxed text-gray-500">
            When a new complaint is routed to your department, an alert is sent to this address. Your login email (
            <span className="font-semibold">{user?.email}</span>) is only for signing in.
          </p>
          <form onSubmit={handleSave} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-bold uppercase tracking-widest text-gray-600">
                Real email inbox
              </label>
              <input
                type="email"
                value={notifEmail}
                onChange={(e) => setNotifEmail(e.target.value)}
                placeholder="yourname@gmail.com"
                className="rounded-xl border border-warm-border px-4 py-3 text-sm text-gray-800 outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <button
              type="submit"
              disabled={saving}
              className="flex items-center justify-center gap-2 rounded-xl bg-primary py-3 text-sm font-bold text-white hover:bg-[#9C4C24] disabled:opacity-60"
            >
              {saved ? (
                <>
                  <CheckCircle size={15} /> Saved!
                </>
              ) : saving ? (
                'Saving…'
              ) : (
                <>
                  <Save size={15} /> Save Changes
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

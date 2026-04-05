import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Bell, Bot, User, GitBranch, FileText, CheckCircle, X } from 'lucide-react'
import { getCurrentUser, getRole, authFetch } from '../utils/auth'
import { ROLE_LABEL } from '../utils/theme'

const LAST_SEEN_KEY = 'admin_notif_last_seen'

function timeAgo(iso) {
  if (!iso) return ''
  const diff = (Date.now() - new Date(iso).getTime()) / 1000
  if (diff < 60)   return 'just now'
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago'
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago'
  return Math.floor(diff / 86400) + 'd ago'
}

const KIND_STYLE = {
  assigned: { icon: <GitBranch size={13} />, bg: '#FFF3EB', color: '#B85C2E' },
  resolved: { icon: <CheckCircle size={13} />, bg: '#F0FDF4', color: '#22C55E' },
  stage:    { icon: <GitBranch size={13} />, bg: '#EFF6FF', color: '#3B82F6' },
  note:     { icon: <FileText size={13} />, bg: '#F5F3FF', color: '#7C3AED' },
  update:   { icon: <GitBranch size={13} />, bg: '#F3F4F6', color: '#6B7280' },
}

export default function Topbar() {
  const navigate    = useNavigate()
  const user        = getCurrentUser()
  const role        = getRole()
  const [search,    setSearch]    = useState('')
  const [open,      setOpen]      = useState(false)
  const [notifs,    setNotifs]    = useState([])
  const [unread,    setUnread]    = useState(0)
  const [loading,   setLoading]   = useState(false)
  const panelRef    = useRef(null)

  const fetchNotifs = useCallback(async () => {
    setLoading(true)
    try {
      const res  = await authFetch('/admin/notifications?limit=20')
      const data = await res.json()
      const items = data.notifications || []
      setNotifs(items)

      const lastSeen = parseInt(localStorage.getItem(LAST_SEEN_KEY) || '0', 10)
      const newCount = items.filter(n => new Date(n.created_at).getTime() > lastSeen).length
      setUnread(newCount)
    } catch {
      // silently fail — notifications are non-critical
    } finally {
      setLoading(false)
    }
  }, [])

  // Fetch on mount and every 60s
  useEffect(() => {
    fetchNotifs()
    const id = setInterval(fetchNotifs, 60_000)
    return () => clearInterval(id)
  }, [fetchNotifs])

  // Close panel on outside click
  useEffect(() => {
    function onClickOutside(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [open])

  function handleBellClick() {
    setOpen(v => !v)
    if (!open) {
      // mark all as read
      localStorage.setItem(LAST_SEEN_KEY, String(Date.now()))
      setUnread(0)
    }
  }

  function handleNotifClick(n) {
    setOpen(false)
    navigate('/complaint-detail/' + n.report_id)
  }

  return (
    <header
      className="h-16 flex items-center justify-between px-6 shrink-0 gap-4"
      style={{ backgroundColor: '#fff', borderBottom: '1px solid #EDE8DC' }}
    >
      {/* Search */}
      <div className="flex items-center gap-3 flex-1 max-w-lg bg-gray-50 rounded-2xl px-4 py-2.5 border border-warm-border transition-all duration-200 focus-within:bg-white focus-within:border-[#B85C2E] focus-within:ring-2 focus-within:ring-[#B85C2E]/20 focus-within:shadow-md">
        <Search size={14} className="text-gray-400 shrink-0" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && search.trim()) navigate('/complaint-management?search=' + encodeURIComponent(search.trim())) }}
          placeholder="Search complaint ID, location, department…"
          className="flex-1 text-sm text-gray-600 placeholder-gray-400 outline-none bg-transparent"
        />
      </div>

      {/* Right */}
      <div className="flex items-center gap-3">

        {/* Bell + dropdown */}
        <div className="relative" ref={panelRef}>
          <button
            onClick={handleBellClick}
            className="w-9 h-9 rounded-xl bg-gray-50 border border-warm-border flex items-center justify-center relative hover:bg-white hover:shadow-sm hover:-translate-y-px active:scale-[0.95] transition-all"
          >
            <Bell size={15} className="text-gray-500" />
            {unread > 0 && (
              <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-primary text-white text-[10px] font-black flex items-center justify-center border-2 border-white">
                {unread > 9 ? '9+' : unread}
              </span>
            )}
            {unread === 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary border-2 border-white" />
            )}
          </button>

          {open && (
            <div
              className="absolute right-0 top-11 w-96 bg-white rounded-2xl shadow-2xl border border-warm-border z-50 overflow-hidden"
              style={{ boxShadow: '0 20px 60px rgba(0,0,0,0.15)' }}
            >
              {/* Header */}
              <div className="flex items-center justify-between px-4 py-3 border-b border-warm-border">
                <div>
                  <p className="text-sm font-black text-gray-900">Notifications</p>
                  <p className="text-xs text-gray-400">Recent activity in your scope</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => { setOpen(false); navigate('/audit-log') }}
                    className="text-xs font-bold text-primary hover:underline"
                  >
                    See all
                  </button>
                  <button onClick={() => setOpen(false)} className="w-6 h-6 rounded-lg bg-gray-100 flex items-center justify-center text-gray-400 hover:bg-gray-200">
                    <X size={12} />
                  </button>
                </div>
              </div>

              {/* List */}
              <div className="overflow-y-auto" style={{ maxHeight: 380 }}>
                {loading && notifs.length === 0 ? (
                  <div className="flex flex-col gap-2 p-3">
                    {[1,2,3].map(i => <div key={i} className="h-14 bg-gray-100 animate-pulse rounded-xl" />)}
                  </div>
                ) : notifs.length === 0 ? (
                  <div className="py-10 text-center text-sm text-gray-400">No activity yet.</div>
                ) : notifs.map((n, i) => {
                  const style  = KIND_STYLE[n.kind] || KIND_STYLE.update
                  const isNew  = unread > 0 && i < unread
                  return (
                    <button
                      key={n.id}
                      onClick={() => handleNotifClick(n)}
                      className="w-full flex items-start gap-3 px-4 py-3 hover:bg-gray-50 border-b last:border-0 border-gray-50 transition-colors text-left"
                      style={{ backgroundColor: isNew ? '#FDFCF0' : undefined }}
                    >
                      {/* Icon */}
                      <div
                        className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                        style={{ backgroundColor: style.bg, color: style.color }}
                      >
                        {n.ai_managed ? <Bot size={13} /> : style.icon}
                      </div>

                      {/* Text */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <span className="text-xs font-black text-gray-800">{n.display_id}</span>
                          {isNew && <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />}
                        </div>
                        <p className="text-xs text-gray-600 leading-snug line-clamp-2">{n.message}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{timeAgo(n.created_at)}</p>
                      </div>
                    </button>
                  )
                })}
              </div>

              {/* Footer */}
              <div className="px-4 py-3 border-t border-warm-border bg-gray-50/50 flex items-center justify-between">
                <p className="text-xs text-gray-400">{notifs.length} recent activities</p>
                <button
                  onClick={fetchNotifs}
                  className="text-xs font-bold text-primary hover:underline"
                  disabled={loading}
                >
                  {loading ? 'Refreshing…' : 'Refresh'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User pill */}
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl cursor-pointer hover:bg-gray-50 hover:shadow-sm hover:-translate-y-px active:scale-[0.98] transition-all border border-transparent hover:border-warm-border"
          onClick={() => navigate('/my-profile')}
        >
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-black text-white shrink-0"
            style={{ backgroundColor: '#B85C2E' }}
          >
            {user?.first_name?.[0]?.toUpperCase() ?? 'A'}
          </div>
          <div className="hidden sm:block">
            <p className="text-xs font-bold text-gray-800 leading-tight">
              {user?.first_name ?? 'Admin'}
            </p>
            <p className="text-xs text-gray-400 leading-tight">
              {ROLE_LABEL[role] ?? 'Admin'}
            </p>
          </div>
        </div>
      </div>
    </header>
  )
}

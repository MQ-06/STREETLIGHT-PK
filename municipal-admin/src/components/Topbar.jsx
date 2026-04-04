import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Bell, Plus } from 'lucide-react'
import { getCurrentUser, getRole } from '../utils/auth'
import { ROLE_LABEL } from '../utils/theme'

/**
 * Topbar — shared top header for all authenticated pages.
 * Props:
 *   showNewReport  bool  — show "New Report" button (default true)
 */
export default function Topbar({ showNewReport = true }) {
  const navigate = useNavigate()
  const user     = getCurrentUser()
  const role     = getRole()
  const [search, setSearch] = useState('')

  return (
    <header
      className="h-16 flex items-center justify-between px-6 shrink-0 gap-4"
      style={{ backgroundColor: '#fff', borderBottom: '1px solid #EDE8DC' }}
    >
      {/* Search */}
      <div className="flex items-center gap-3 flex-1 max-w-lg bg-gray-50 rounded-2xl px-4 py-2.5 border border-warm-border">
        <Search size={14} className="text-gray-400 shrink-0" />
        <input
          type="text"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search complaint ID, location, department…"
          className="flex-1 text-sm text-gray-600 placeholder-gray-400 outline-none bg-transparent"
        />
      </div>

      {/* Right */}
      <div className="flex items-center gap-3">
        {/* Bell */}
        <button
          className="w-9 h-9 rounded-xl bg-gray-50 border border-warm-border flex items-center justify-center relative hover:bg-white transition-colors"
          onClick={() => navigate('/complaint-management')}
        >
          <Bell size={15} className="text-gray-500" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary border-2 border-white" />
        </button>

        {/* New report */}
        {showNewReport && (
          <button
            onClick={() => navigate('/complaint-management')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark transition-colors shadow-sm shadow-primary/20"
          >
            <Plus size={14} />
            New Report
          </button>
        )}

        {/* User pill */}
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl cursor-pointer hover:bg-gray-50 transition-colors"
          onClick={() => navigate('/user-roles')}
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

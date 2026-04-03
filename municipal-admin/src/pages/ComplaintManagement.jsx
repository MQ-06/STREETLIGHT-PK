import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Bell, Plus, Filter, Search, ChevronDown, Eye, Timer, Smile } from 'lucide-react'
import { authFetch } from '../utils/auth'

const NAV_LINKS = [
  { label: 'Complaints',  path: '/complaint-management' },
  { label: 'Analytics',   path: '/analytics' },
  { label: 'Departments', path: '/departments' },
]

const STAGE_OPTIONS = [
  { label: 'New',                  value: 'NEW' },
  { label: 'Pending Verification', value: 'PENDING_VERIFICATION' },
  { label: 'Verified',             value: 'VERIFIED' },
  { label: 'In Progress',          value: 'IN_PROGRESS' },
  { label: 'Awaiting Feedback',    value: 'AWAITING_FEEDBACK' },
  { label: 'Resolved',             value: 'RESOLVED' },
]

export default function ComplaintManagement() {
  const navigate = useNavigate()
  const location = useLocation()

  const [searchVal,    setSearchVal]    = useState('')
  const [stageFilter,  setStageFilter]  = useState('')
  const [dateRange,    setDateRange]    = useState('')
  const [activePage,   setActivePage]   = useState(1)
  const [complaints,   setComplaints]   = useState([])
  const [total,        setTotal]        = useState(0)
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState(null)

  const LIMIT = 20

  const fetchComplaints = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const skip   = (activePage - 1) * LIMIT
      const params = new URLSearchParams({ skip, limit: LIMIT })
      if (stageFilter)  params.set('stage',  stageFilter)
      if (searchVal.trim()) params.set('search', searchVal.trim())

      const res  = await authFetch(`/admin/reports?${params}`)
      const data = await res.json()
      setComplaints(data.reports || [])
      setTotal(data.total || 0)
    } catch (e) {
      setError('Failed to load complaints.')
    } finally {
      setLoading(false)
    }
  }, [activePage, stageFilter, searchVal])

  useEffect(() => { fetchComplaints() }, [fetchComplaints])

  const totalPages = Math.max(1, Math.ceil(total / LIMIT))

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-8 bg-white border-b border-gray-100 shrink-0">
        {/* Logo → dashboard */}
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => navigate('/dashboard')}
        >
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#ede8dc' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#b85c2a" />
              <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#b85c2a" />
              <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#b85c2a" />
              <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#b85c2a" />
            </svg>
          </div>
          <span className="font-extrabold text-sm tracking-widest uppercase" style={{ color: '#b85c2a' }}>
            Streetlight
          </span>
        </div>

        {/* Nav */}
        <nav className="flex items-center gap-8">
          {NAV_LINKS.map(({ label, path }) => (
            <button
              key={label}
              onClick={() => navigate(path)}
              className="text-sm font-medium pb-1 transition-colors"
              style={{
                color: location.pathname === path ? '#b85c2a' : '#6b7280',
                borderBottom: location.pathname === path ? '2px solid #b85c2a' : '2px solid transparent',
              }}
            >
              {label}
            </button>
          ))}
        </nav>

        {/* Right */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/complaint-management')}
            className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center"
          >
            <Bell size={16} className="text-gray-600" />
          </button>
          <img
            src="https://i.pravatar.cc/36?img=1"
            alt="user"
            className="w-9 h-9 rounded-full object-cover cursor-pointer"
            onClick={() => navigate('/user-roles')}
          />
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="flex-1 overflow-y-auto px-8 py-6 flex flex-col gap-5">

        {/* Page header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">Complaint Management</h1>
            <p className="text-sm text-gray-500 mt-1">Manage and track municipal issues reported by citizens.</p>
          </div>
          {/* New Complaint → complaint-detail */}
          <button
            onClick={() => navigate('/complaint-detail')}
            className="flex items-center gap-2 px-5 py-3 rounded-full text-white text-sm font-semibold shadow-sm"
            style={{ backgroundColor: '#b85c2a' }}
          >
            <Plus size={15} /> New Complaint
          </button>
        </div>

        {/* ── MAIN ROW ── */}
        <div className="flex gap-5 flex-1">

          {/* ── LEFT SIDEBAR ── */}
          <div className="w-64 shrink-0 flex flex-col gap-4">

            {/* Filters card */}
            <div className="bg-white rounded-2xl p-5 shadow-sm flex flex-col gap-4">
              <div className="flex items-center gap-2">
                <Filter size={15} className="text-gray-700" />
                <span className="font-extrabold text-gray-800">Filters</span>
              </div>

              {/* Search */}
              <div>
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Search ID or Type</p>
                <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-3 py-2.5">
                  <Search size={13} className="text-gray-400 shrink-0" />
                  <input
                    type="text"
                    placeholder="e.g. #SR-9921"
                    value={searchVal}
                    onChange={e => setSearchVal(e.target.value)}
                    className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
                  />
                </div>
              </div>

              {/* Stage */}
              <div>
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Stage</p>
                <div className="relative">
                  <select
                    value={stageFilter}
                    onChange={e => { setStageFilter(e.target.value); setActivePage(1) }}
                    className="w-full bg-gray-100 rounded-xl px-3 py-2.5 text-sm text-gray-700 outline-none appearance-none cursor-pointer"
                  >
                    <option value="">All Stages</option>
                    {STAGE_OPTIONS.map(o => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                  <ChevronDown size={13} className="absolute right-3 top-3 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* Date Range */}
              <div>
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Date Range</p>
                <input
                  type="date"
                  value={dateRange}
                  onChange={e => setDateRange(e.target.value)}
                  className="w-full bg-gray-100 rounded-xl px-3 py-2.5 text-sm text-gray-500 outline-none"
                />
              </div>

              {/* Reset */}
              <button
                onClick={() => {
                  setSearchVal('')
                  setStageFilter('')
                  setDateRange('')
                  setActivePage(1)
                }}
                className="w-full py-2.5 rounded-xl text-sm font-semibold border transition-colors hover:bg-gray-50"
                style={{ color: '#b85c2a', borderColor: '#e5e7eb' }}
              >
                Reset All Filters
              </button>
            </div>

            {/* Active Tickets card */}
            <div
              className="bg-white rounded-2xl p-5 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate('/analytics')}
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Total Loaded</p>
              </div>
              <p className="text-4xl font-extrabold text-gray-900 mb-3">{total}</p>
              <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
                <div className="h-full rounded-full" style={{ backgroundColor: '#b85c2a', width: '60%' }} />
              </div>
            </div>
          </div>

          {/* ── RIGHT CONTENT ── */}
          <div className="flex-1 flex flex-col gap-4">

            {/* Table card */}
            <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
              <table className="w-full">
                <thead>
                  <tr style={{ borderBottom: '1px solid #f3f4f6' }}>
                    {['COMPLAINT ID', 'ISSUE TYPE', 'DEPARTMENT', 'SEVERITY', 'STATUS', 'ACTION'].map(h => (
                      <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-5 py-4">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="px-5 py-10 text-center text-sm text-gray-400">
                        Loading…
                      </td>
                    </tr>
                  ) : error ? (
                    <tr>
                      <td colSpan={6} className="px-5 py-10 text-center text-sm text-red-500">
                        {error}
                      </td>
                    </tr>
                  ) : complaints.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-5 py-10 text-center text-sm text-gray-400">
                        No complaints found.
                      </td>
                    </tr>
                  ) : complaints.map(c => (
                    <tr
                      key={c.id}
                      className="border-b last:border-0 hover:bg-gray-50 transition-colors cursor-pointer"
                      style={{ borderColor: '#f9f9f9' }}
                      onClick={() => navigate(`/complaint-detail/${c.id}`)}
                    >
                      <td className="px-5 py-4">
                        <span className="text-sm font-extrabold text-gray-800">{c.display_id}</span>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-base shrink-0"
                            style={{ backgroundColor: '#fff7ed' }}>
                            {c.icon}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-800">{c.title}</p>
                            <p className="text-xs text-gray-400">{c.location}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-sm text-gray-600 capitalize">
                        {c.assigned_department ?? '—'}
                      </td>
                      <td className="px-5 py-4">
                        <span
                          className="text-xs font-bold px-3 py-1 rounded-full"
                          style={{ backgroundColor: c.severity_bg, color: c.severity_color }}
                        >
                          {c.severity}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.stage_dot }} />
                          <span className="text-sm font-medium" style={{ color: c.stage_dot }}>
                            {c.kanban_stage.replace(/_/g, ' ')}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <button
                          onClick={e => { e.stopPropagation(); navigate(`/complaint-detail/${c.id}`) }}
                          className="text-gray-400 hover:text-gray-600 transition-colors"
                        >
                          <Eye size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Pagination */}
              <div className="flex items-center justify-between px-5 py-4" style={{ borderTop: '1px solid #f3f4f6' }}>
                <p className="text-sm text-gray-500">
                  Showing{' '}
                  <span className="font-bold text-gray-800">
                    {Math.min((activePage - 1) * LIMIT + 1, total)} – {Math.min(activePage * LIMIT, total)}
                  </span>{' '}
                  of <span className="font-bold text-gray-800">{total}</span> complaints
                </p>
                <div className="flex items-center gap-1.5">
                  <button
                    disabled={activePage === 1}
                    onClick={() => setActivePage(p => Math.max(1, p - 1))}
                    className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-40"
                  >
                    Previous
                  </button>
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
                    <button
                      key={p}
                      onClick={() => setActivePage(p)}
                      className="w-8 h-8 rounded-lg text-sm font-bold transition-all"
                      style={{
                        backgroundColor: activePage === p ? '#b85c2a' : 'transparent',
                        color:           activePage === p ? '#fff'    : '#6b7280',
                      }}
                    >
                      {p}
                    </button>
                  ))}
                  <button
                    disabled={activePage === totalPages}
                    onClick={() => setActivePage(p => Math.min(totalPages, p + 1))}
                    className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>

            {/* ── BOTTOM STATS ── */}
            <div className="grid grid-cols-2 gap-4">
              {/* Resolution Speed → analytics */}
              <div
                className="bg-white rounded-2xl p-5 shadow-sm flex items-center justify-between cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate('/analytics')}
              >
                <div>
                  <p className="text-sm font-bold text-gray-800">Resolution Speed</p>
                  <p className="text-xs text-gray-400 mb-3">Average time to close a ticket</p>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-extrabold text-gray-900">42.5 hrs</span>
                    <span className="text-xs font-bold text-green-500 mb-1">↓ 4%</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#fff7ed' }}>
                  <Timer size={20} style={{ color: '#b85c2a' }} />
                </div>
              </div>

              {/* Citizen Satisfaction → analytics */}
              <div
                className="bg-white rounded-2xl p-5 shadow-sm flex items-center justify-between cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate('/analytics')}
              >
                <div>
                  <p className="text-sm font-bold text-gray-800">Citizen Satisfaction</p>
                  <p className="text-xs text-gray-400 mb-3">Based on resolution feedback</p>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-extrabold text-gray-900">4.8/5.0</span>
                    <span className="text-xs font-bold mb-1" style={{ color: '#b85c2a' }}>★ Top City</span>
                  </div>
                </div>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#fff7ed' }}>
                  <Smile size={20} style={{ color: '#b85c2a' }} />
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-400 py-2">
          © 2024 Streetlight Civic Management System. Built for a smarter future.
        </p>

      </div>
    </div>
  )
}
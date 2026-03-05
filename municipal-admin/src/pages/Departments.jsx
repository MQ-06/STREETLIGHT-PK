import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Bell, Plus, Filter, Search, ChevronDown, Eye, Timer, Smile } from 'lucide-react'

const NAV_LINKS = [
  { label: 'Complaints',  path: '/complaint-management' },
  { label: 'Analytics',   path: '/analytics' },
  { label: 'Departments', path: '/departments' },
  { label: 'Settings',    path: '/settings' },
]

const COMPLAINTS = [
  {
    id: '#SR-9921',
    icon: '💡',
    iconBg: '#fff7ed',
    title: 'Broken Streetlight',
    location: '5th Ave, Downtown',
    department: 'Electricity',
    severity: 'High',
    severityBg: '#fef2f2',
    severityColor: '#ef4444',
    status: 'In Progress',
    statusDot: '#f97316',
    statusColor: '#f97316',
  },
  {
    id: '#SR-9922',
    icon: '💧',
    iconBg: '#eff6ff',
    title: 'Water Leakage',
    location: 'Main Square',
    department: 'Public Works',
    severity: 'Medium',
    severityBg: '#fff7ed',
    severityColor: '#f97316',
    status: 'Pending Review',
    statusDot: '#f97316',
    statusColor: '#f97316',
  },
  {
    id: '#SR-9920',
    icon: '🎨',
    iconBg: '#f0fdf4',
    title: 'Graffiti Removal',
    location: 'Park Lane',
    department: 'Sanitation',
    severity: 'Low',
    severityBg: '#f0fdf4',
    severityColor: '#22c55e',
    status: 'Resolved',
    statusDot: '#22c55e',
    statusColor: '#22c55e',
  },
  {
    id: '#SR-9918',
    icon: '🔧',
    iconBg: '#faf5ff',
    title: 'Major Pothole',
    location: 'Bridge Road',
    department: 'Urban Planning',
    severity: 'High',
    severityBg: '#fef2f2',
    severityColor: '#ef4444',
    status: 'In Progress',
    statusDot: '#f97316',
    statusColor: '#f97316',
  },
]

const STATUS_OPTIONS = ['In Progress', 'Pending Review', 'Resolved']

export default function ComplaintManagement() {
  const navigate = useNavigate()
  const location = useLocation()

  const [searchVal, setSearchVal]   = useState('')
  const [statuses, setStatuses]     = useState(['In Progress', 'Pending Review'])
  const [department, setDepartment] = useState('All Departments')
  const [dateRange, setDateRange]   = useState('')
  const [activePage, setActivePage] = useState(1)

  const toggleStatus = (s) => {
    setStatuses(prev =>
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    )
  }

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

              {/* Status */}
              <div>
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Status</p>
                <div className="flex flex-col gap-2">
                  {STATUS_OPTIONS.map(s => (
                    <label key={s} className="flex items-center gap-2 cursor-pointer">
                      <div
                        onClick={() => toggleStatus(s)}
                        className="w-5 h-5 rounded-full flex items-center justify-center shrink-0 cursor-pointer transition-all"
                        style={{
                          backgroundColor: statuses.includes(s) ? '#b85c2a' : 'transparent',
                          border: statuses.includes(s) ? 'none' : '2px solid #d1d5db',
                        }}
                      >
                        {statuses.includes(s) && (
                          <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                            <path d="M2 6l3 3 5-5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                        )}
                      </div>
                      <span className="text-sm text-gray-700">{s}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Department */}
              <div>
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Department</p>
                <div className="relative">
                  <select
                    value={department}
                    onChange={e => setDepartment(e.target.value)}
                    className="w-full bg-gray-100 rounded-xl px-3 py-2.5 text-sm text-gray-700 outline-none appearance-none cursor-pointer"
                  >
                    <option>All Departments</option>
                    <option>Electricity</option>
                    <option>Public Works</option>
                    <option>Sanitation</option>
                    <option>Urban Planning</option>
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
                  setStatuses(['In Progress', 'Pending Review'])
                  setDepartment('All Departments')
                  setDateRange('')
                }}
                className="w-full py-2.5 rounded-xl text-sm font-semibold border transition-colors hover:bg-gray-50"
                style={{ color: '#b85c2a', borderColor: '#e5e7eb' }}
              >
                Reset All Filters
              </button>
            </div>

            {/* Active Tickets card — click → analytics */}
            <div
              className="bg-white rounded-2xl p-5 shadow-sm cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate('/analytics')}
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">Active Tickets</p>
                <span className="text-xs font-bold text-green-500">+12%</span>
              </div>
              <p className="text-4xl font-extrabold text-gray-900 mb-3">482</p>
              <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
                <div className="h-full rounded-full w-2/5" style={{ backgroundColor: '#b85c2a' }} />
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
                  {COMPLAINTS.map((c, i) => (
                    <tr
                      key={i}
                      className="border-b last:border-0 hover:bg-gray-50 transition-colors cursor-pointer"
                      style={{ borderColor: '#f9f9f9' }}
                      onClick={() => navigate('/complaint-detail')}
                    >
                      <td className="px-5 py-4">
                        <span className="text-sm font-extrabold text-gray-800">{c.id}</span>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-base shrink-0"
                            style={{ backgroundColor: c.iconBg }}>
                            {c.icon}
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-800">{c.title}</p>
                            <p className="text-xs text-gray-400">{c.location}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-sm text-gray-600">{c.department}</td>
                      <td className="px-5 py-4">
                        <span
                          className="text-xs font-bold px-3 py-1 rounded-full"
                          style={{ backgroundColor: c.severityBg, color: c.severityColor }}
                        >
                          {c.severity}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.statusDot }} />
                          <span className="text-sm font-medium" style={{ color: c.statusColor }}>{c.status}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <button
                          onClick={e => { e.stopPropagation(); navigate('/complaint-detail') }}
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
                  Showing <span className="font-bold text-gray-800">1 – 10</span> of{' '}
                  <span className="font-bold text-gray-800">2,482</span> complaints
                </p>
                <div className="flex items-center gap-1.5">
                  <button className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700">Previous</button>
                  {[1, 2, 3].map(p => (
                    <button
                      key={p}
                      onClick={() => setActivePage(p)}
                      className="w-8 h-8 rounded-lg text-sm font-bold transition-all"
                      style={{
                        backgroundColor: activePage === p ? '#b85c2a' : 'transparent',
                        color: activePage === p ? '#fff' : '#6b7280',
                      }}
                    >
                      {p}
                    </button>
                  ))}
                  <span className="text-gray-400 text-sm">...</span>
                  <button
                    onClick={() => setActivePage(248)}
                    className="w-8 h-8 rounded-lg text-sm font-bold text-gray-500 hover:bg-gray-100"
                  >
                    248
                  </button>
                  <button className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700">Next</button>
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
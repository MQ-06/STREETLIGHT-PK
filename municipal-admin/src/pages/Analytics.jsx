import { useNavigate, useLocation } from 'react-router-dom'
import { Bell, Calendar, Download, MapPin, TrendingUp, TrendingDown } from 'lucide-react'

const NAV_LINKS = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Analytics', path: '/analytics' },
  { label: 'Issues',    path: '/resolution-board' },
  { label: 'Settings',  path: '/settings' },
]

const STATS = [
  { icon: '📋', iconBg: '#fff7ed', change: '+12.4%', changeColor: '#22c55e', label: 'Total Reports',        value: '2,482'    },
  { icon: '✅', iconBg: '#f0fdf4', change: '+8.1%',  changeColor: '#22c55e', label: 'Resolution Rate',      value: '94.2%'    },
  { icon: '⏱', iconBg: '#eff6ff', change: '-2.4h',  changeColor: '#ef4444', label: 'Avg. Resolution Time', value: '18.5 hrs' },
  { icon: '⭐', iconBg: '#fefce8', change: '+0.4',   changeColor: '#22c55e', label: 'Citizen Satisfaction', value: '4.8 / 5.0'},
]

const BREAKDOWN = [
  { label: 'Streetlights',     pct: 35, color: '#b85c2a' },
  { label: 'Waste Management', pct: 25, color: '#eab308' },
  { label: 'Road & Potholes',  pct: 20, color: '#22c55e' },
  { label: 'Water Supply',     pct: 20, color: '#3b82f6' },
]

const DEPARTMENTS = [
  { name: 'Infrastructure',     hrs: 12.4, pct: 50 },
  { name: 'Electricity Dept.',  hrs: 18.2, pct: 68 },
  { name: 'Waste & Sanitation', hrs: 24.5, pct: 90 },
  { name: 'Parks & Recreation', hrs: 9.1,  pct: 38 },
  { name: 'Public Safety',      hrs: 14.8, pct: 58 },
]

const PROBLEM_AREAS = [
  {
    location: '5th Avenue, Downtown',
    issue: 'Broken Streetlights',
    freq: '12 reports/mo',
    trend: '+15%', trendUp: true,
    status: 'High Alert', statusBg: '#fff7ed', statusColor: '#f97316',
  },
  {
    location: 'Park Lane Crossing',
    issue: 'Illegal Dumping',
    freq: '8 reports/mo',
    trend: '-4%', trendUp: false,
    status: 'Monitoring', statusBg: '#f3f4f6', statusColor: '#6b7280',
  },
  {
    location: 'Industrial Zone East',
    issue: 'Water Leakage',
    freq: '21 reports/mo',
    trend: '+32%', trendUp: true,
    status: 'Critical', statusBg: '#fef2f2', statusColor: '#ef4444',
  },
]

function DonutChart() {
  const segments = [
    { pct: 35, color: '#b85c2a' },
    { pct: 25, color: '#eab308' },
    { pct: 20, color: '#22c55e' },
    { pct: 20, color: '#3b82f6' },
  ]
  const r = 68
  const cx = 88
  const cy = 88
  const circumference = 2 * Math.PI * r
  const gap = 3
  let offset = 0
  const slices = segments.map((s) => {
    const dash = (s.pct / 100) * circumference - gap
    const slice = { ...s, dash, offset }
    offset += (s.pct / 100) * circumference
    return slice
  })

  return (
    <svg width="176" height="176" viewBox="0 0 176 176">
      {slices.map((s, i) => (
        <circle
          key={i}
          cx={cx} cy={cy} r={r}
          fill="none"
          stroke={s.color}
          strokeWidth="20"
          strokeDasharray={`${s.dash} ${circumference - s.dash}`}
          strokeDashoffset={-s.offset + circumference * 0.25}
        />
      ))}
      <text x={cx} y={cy - 6}  textAnchor="middle" fontSize="24" fontWeight="800" fill="#111827">100%</text>
      <text x={cx} y={cy + 12} textAnchor="middle" fontSize="8"  fontWeight="600" fill="#9ca3af" letterSpacing="1.5">TOTAL VOLUME</text>
    </svg>
  )
}

export default function Analytics() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-8 bg-white shadow-sm shrink-0">
        {/* Logo → Dashboard */}
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

        {/* Nav links */}
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

        {/* Right — Bell → complaint-management, Avatar → dashboard */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/complaint-management')}
            className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center"
          >
            <Bell size={16} className="text-gray-600" />
          </button>
          <img
            src="https://i.pravatar.cc/36?img=1"
            alt="admin"
            className="w-9 h-9 rounded-full object-cover cursor-pointer"
            onClick={() => navigate('/user-roles')}
          />
          <div className="cursor-pointer" onClick={() => navigate('/user-roles')}>
            <p className="text-sm font-bold text-gray-800 leading-tight">City Admin</p>
            <p className="text-xs text-gray-400">Metropolitan District</p>
          </div>
        </div>
      </header>

      {/* ── PAGE CONTENT ── */}
      <div className="flex-1 px-8 py-7 flex flex-col gap-6 overflow-y-auto">

        {/* Page header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900">Analytics & Performance</h1>
            <p className="text-sm text-gray-500 mt-1">Real-time insights into municipal efficiency and public engagement.</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white shadow-sm text-sm font-medium text-gray-600 border border-gray-100">
              <Calendar size={14} /> Last 30 Days
            </button>
            {/* Export → downloads (no nav needed, stays on page) */}
            <button
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-sm font-semibold"
              style={{ backgroundColor: '#b85c2a' }}
            >
              <Download size={14} /> Export Report
            </button>
          </div>
        </div>

        {/* ── STAT CARDS — click → complaint-management ── */}
        <div className="grid grid-cols-4 gap-4">
          {STATS.map((s) => (
            <div
              key={s.label}
              className="bg-white rounded-2xl p-5 shadow-sm flex flex-col gap-3 cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => navigate('/complaint-management')}
            >
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg" style={{ backgroundColor: s.iconBg }}>
                  {s.icon}
                </div>
                <span className="text-xs font-bold" style={{ color: s.changeColor }}>{s.change}</span>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">{s.label}</p>
                <p className="text-2xl font-extrabold text-gray-900">{s.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ── MIDDLE ROW ── */}
        <div className="flex gap-5">

          {/* Complaint Breakdown — click items → complaint-management */}
          <div className="bg-white rounded-2xl p-6 shadow-sm shrink-0" style={{ width: 300 }}>
            <h2 className="text-base font-extrabold text-gray-900 mb-5">Complaint Breakdown</h2>
            <div className="flex justify-center mb-5">
              <DonutChart />
            </div>
            <div className="flex flex-col gap-3">
              {BREAKDOWN.map((b) => (
                <div
                  key={b.label}
                  className="flex items-center justify-between cursor-pointer hover:opacity-70"
                  onClick={() => navigate('/complaint-management')}
                >
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: b.color }} />
                    <span className="text-sm text-gray-600">{b.label}</span>
                  </div>
                  <span className="text-sm font-bold text-gray-700">{b.pct}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Department Resolution Times — click rows → departments */}
          <div className="flex-1 bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-base font-extrabold text-gray-900">Department Resolution Times (Hrs)</h2>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-400" />
                <span className="text-xs font-bold text-gray-400 tracking-widest">TARGET</span>
              </div>
            </div>
            <div className="flex flex-col gap-5">
              {DEPARTMENTS.map((d) => (
                <div
                  key={d.name}
                  className="cursor-pointer hover:opacity-70"
                  onClick={() => navigate('/departments')}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-700">{d.name}</span>
                    <span className="text-sm font-bold text-gray-800">{d.hrs}h</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${d.pct}%`, backgroundColor: '#b85c2a' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── RECURRING PROBLEM AREAS ── */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-lg font-extrabold text-gray-900">Recurring Problem Areas</h2>
            {/* View Map View → hotspot-map */}
            <button
              onClick={() => navigate('/hotspot-map')}
              className="text-sm font-bold"
              style={{ color: '#b85c2a' }}
            >
              View Map View
            </button>
          </div>

          <table className="w-full mt-4">
            <thead>
              <tr className="text-left border-b" style={{ borderColor: '#f3f4f6' }}>
                {['Location', 'Primary Issue', 'Incident Frequency', 'Trend', 'Status'].map(h => (
                  <th key={h} className="text-xs font-medium text-gray-400 pb-3 pr-6">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PROBLEM_AREAS.map((row, i) => (
                // Row click → complaint-detail
                <tr
                  key={i}
                  className="border-b last:border-0 cursor-pointer hover:bg-gray-50"
                  style={{ borderColor: '#f9f9f9' }}
                  onClick={() => navigate('/complaint-detail')}
                >
                  <td className="py-5 pr-6">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center">
                        <MapPin size={12} className="text-gray-400" />
                      </div>
                      <span className="text-sm text-gray-800">{row.location}</span>
                    </div>
                  </td>
                  <td className="py-5 pr-6 text-sm text-gray-600">{row.issue}</td>
                  <td className="py-5 pr-6 text-sm text-gray-600">{row.freq}</td>
                  <td className="py-5 pr-6">
                    <div className="flex items-center gap-1 text-sm font-bold" style={{ color: row.trendUp ? '#ef4444' : '#22c55e' }}>
                      {row.trendUp ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                      {row.trend}
                    </div>
                  </td>
                  <td className="py-5">
                    <span className="text-xs font-bold px-3 py-1 rounded-full" style={{ backgroundColor: row.statusBg, color: row.statusColor }}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  )
}
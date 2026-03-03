import { useState } from 'react'
import {
  FileText, ClipboardList, Map, Users, BarChart2,
  Bell, Plus, Search, ChevronDown, MoreHorizontal,
  Zap, CheckCircle, UserCircle, TrendingUp
} from 'lucide-react'

const SIDEBAR_LINKS = [
  { label: 'Overview',        icon: BarChart2,     active: true },
  { label: 'All Complaints',  icon: ClipboardList, active: false },
  { label: 'Live Map',        icon: Map,           active: false },
  { label: 'Department',      icon: Users,         active: false },
  { label: 'Impact Reports',  icon: FileText,      active: false },
]

const STATS = [
  {
    label: 'Total Complaints',
    value: '1,284',
    badge: '+12.4%',
    badgeColor: '#22c55e',
    icon: FileText,
    iconBg: '#f3f4f6',
    iconColor: '#6b7280',
    barColor: '#d1d5db',
    barWidth: '60%',
    dark: false,
  },
  {
    label: 'Pending',
    value: '156',
    badge: 'High',
    badgeColor: '#f97316',
    icon: ClipboardList,
    iconBg: '#fff7ed',
    iconColor: '#f97316',
    barColor: '#f97316',
    barWidth: '30%',
    dark: false,
  },
  {
    label: 'In Progress',
    value: '342',
    badge: 'Active',
    badgeColor: '#3b82f6',
    icon: Users,
    iconBg: '#eff6ff',
    iconColor: '#3b82f6',
    barColor: '#3b82f6',
    barWidth: '50%',
    dark: false,
  },
  {
    label: 'Resolved',
    value: '786',
    badge: 'Goal Met',
    badgeColor: '#fff',
    icon: CheckCircle,
    iconBg: 'rgba(255,255,255,0.2)',
    iconColor: '#fff',
    barColor: 'rgba(255,255,255,0.4)',
    barWidth: '75%',
    dark: true,
  },
]

const ACTIVITY = [
  {
    id: 1,
    icon: Zap,
    iconBg: '#fff3eb',
    iconColor: '#b85c2a',
    title: 'New Complaint: #SR-9921',
    sub: 'Broken Streetlight – 5th Ave',
    time: '2 MINUTES AGO',
  },
  {
    id: 2,
    icon: CheckCircle,
    iconBg: '#dcfce7',
    iconColor: '#22c55e',
    title: 'Resolved: #SR-9874',
    sub: 'Pot-hole repair – North Square',
    time: '45 MINUTES AGO',
  },
  {
    id: 3,
    icon: UserCircle,
    iconBg: '#eff6ff',
    iconColor: '#3b82f6',
    title: 'Technician Assigned',
    sub: 'Team Alpha to Park Lane project',
    time: '2 HOURS AGO',
  },
]

const COMPLAINTS = [
  {
    id: '#SR-9921',
    desc: 'Broken Streetlight',
    location: '5th Ave, Downtown',
    priority: 'HIGH',
    priorityBg: '#fef2f2',
    priorityColor: '#ef4444',
    status: 'In Progress',
    statusDot: '#f97316',
    avatars: [
      'https://i.pravatar.cc/28?img=1',
      'https://i.pravatar.cc/28?img=2',
    ],
    extra: '+12',
  },
]

const DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
const BAR_HEIGHTS = [40, 65, 50, 80, 55, 70, 45]

export default function Dashboard() {
  const [activeLink, setActiveLink] = useState('Overview')
  const [period, setPeriod] = useState('Last 7 days')

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── SIDEBAR ── */}
      <aside className="w-60 shrink-0 flex flex-col" style={{ backgroundColor: '#f7f6e8', borderRight: '1px solid #ede8dc' }}>

        {/* Logo */}
        <div className="flex items-center gap-2 px-5 py-5">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#b85c2a' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
              <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#fff" />
              <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#fff" />
              <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#fff" />
              <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#fff" />
            </svg>
          </div>
          <span className="font-extrabold text-lg" style={{ color: '#b85c2a' }}>Streetlight</span>
        </div>

        {/* Nav links */}
        <nav className="flex-1 px-3 flex flex-col gap-1 mt-2">
          {SIDEBAR_LINKS.map(({ label, icon: Icon }) => (
            <button
              key={label}
              onClick={() => setActiveLink(label)}
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all w-full text-left"
              style={{
                backgroundColor: activeLink === label ? '#b85c2a' : 'transparent',
                color: activeLink === label ? '#fff' : '#6b7280',
              }}
            >
              <Icon size={17} />
              {label}
            </button>
          ))}
        </nav>

        {/* User profile */}
        <div className="px-4 py-5 border-t" style={{ borderColor: '#ede8dc' }}>
          <p className="text-xs text-gray-400 uppercase tracking-widest mb-2">Logged In As</p>
          <div className="flex items-center gap-3">
            <img src="https://i.pravatar.cc/36?img=1" alt="user" className="w-9 h-9 rounded-full object-cover" />
            <div>
              <p className="text-sm font-bold text-gray-800">Alex Johnson</p>
              <p className="text-xs text-gray-400">Municipal Officer</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ── MAIN ── */}
      <div className="flex-1 flex flex-col overflow-hidden">

        {/* Top bar */}
        <header className="h-16 bg-white flex items-center justify-between px-6 shrink-0 shadow-sm">
          <div className="flex items-center gap-3 flex-1 max-w-lg">
            <Search size={15} className="text-gray-400 shrink-0" />
            <input
              type="text"
              placeholder="Search for complaint ID, location, or department..."
              className="flex-1 text-sm text-gray-600 placeholder-gray-400 outline-none bg-transparent"
            />
          </div>
          <div className="flex items-center gap-3">
            <button className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center relative">
              <Bell size={16} className="text-gray-600" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500" />
            </button>
            <button
              className="flex items-center gap-2 px-5 py-2.5 rounded-full text-white text-sm font-semibold"
              style={{ backgroundColor: '#b85c2a' }}
            >
              <Plus size={14} /> New Report
            </button>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-5">

          {/* ── STAT CARDS ── */}
          <div className="grid grid-cols-4 gap-4">
            {STATS.map((s) => {
              const Icon = s.icon
              return (
                <div
                  key={s.label}
                  className="rounded-2xl p-5 flex flex-col gap-3 shadow-sm"
                  style={{
                    backgroundColor: s.dark ? '#b85c2a' : '#fff',
                    color: s.dark ? '#fff' : '#111',
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: s.iconBg }}>
                      <Icon size={18} style={{ color: s.iconColor }} />
                    </div>
                    <span className="text-xs font-bold" style={{ color: s.badgeColor }}>
                      {s.badge}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs font-medium mb-1" style={{ color: s.dark ? 'rgba(255,255,255,0.7)' : '#9ca3af' }}>
                      {s.label}
                    </p>
                    <p className="text-3xl font-extrabold">{s.value}</p>
                  </div>
                  <div className="h-1 rounded-full w-full" style={{ backgroundColor: s.dark ? 'rgba(255,255,255,0.2)' : '#f3f4f6' }}>
                    <div className="h-full rounded-full" style={{ width: s.barWidth, backgroundColor: s.barColor }} />
                  </div>
                </div>
              )
            })}
          </div>

          {/* ── MIDDLE ROW ── */}
          <div className="flex gap-4">

            {/* Complaint Trends */}
            <div className="flex-1 bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h2 className="text-lg font-extrabold text-gray-900">Complaint Trends</h2>
                  <p className="text-xs text-gray-400 mt-0.5">Weekly resolution statistics</p>
                </div>
                <button className="flex items-center gap-2 text-sm text-gray-600 bg-gray-100 px-3 py-1.5 rounded-lg">
                  {period} <ChevronDown size={13} />
                </button>
              </div>

              {/* Bar chart */}
              <div className="flex items-end justify-between gap-3 h-44 px-2">
                {DAYS.map((day, i) => (
                  <div key={day} className="flex flex-col items-center gap-2 flex-1">
                    <div className="w-full rounded-t-lg transition-all" style={{
                      height: `${BAR_HEIGHTS[i]}%`,
                      backgroundColor: i === 3 ? '#b85c2a' : '#f0ede6',
                    }} />
                    <span className="text-xs text-gray-400 font-medium">{day}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="w-72 bg-white rounded-2xl p-5 shadow-sm shrink-0">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-extrabold text-gray-900">Recent Activity</h2>
                <button className="text-xs font-bold" style={{ color: '#b85c2a' }}>View All</button>
              </div>
              <div className="flex flex-col gap-4">
                {ACTIVITY.map(({ id, icon: Icon, iconBg, iconColor, title, sub, time }) => (
                  <div key={id} className="flex gap-3">
                    <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: iconBg }}>
                      <Icon size={16} style={{ color: iconColor }} />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-800 leading-snug">{title}</p>
                      <p className="text-xs text-gray-500">{sub}</p>
                      <p className="text-xs text-gray-400 mt-0.5 tracking-wide">{time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ── LIVE COMPLAINT MONITORING ── */}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-extrabold text-gray-900">Live Complaint Monitoring</h2>
              <div className="flex gap-2">
                <button className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200">
                  Filters
                </button>
                <button className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200">
                  Export
                </button>
              </div>
            </div>

            {/* Table */}
            <table className="w-full">
              <thead>
                <tr className="text-left">
                  {['COMPLAINT ID', 'DESCRIPTION', 'PRIORITY', 'STATUS', 'SUPPORTERS', ''].map(h => (
                    <th key={h} className="text-xs font-bold text-gray-400 tracking-widest pb-3 pr-4">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {COMPLAINTS.map(c => (
                  <tr key={c.id} className="border-t" style={{ borderColor: '#f3f4f6' }}>
                    <td className="py-4 pr-4 text-sm font-bold text-gray-800">{c.id}</td>
                    <td className="py-4 pr-4">
                      <p className="text-sm font-semibold text-gray-800">{c.desc}</p>
                      <p className="text-xs text-gray-400">{c.location}</p>
                    </td>
                    <td className="py-4 pr-4">
                      <span
                        className="text-xs font-bold px-2.5 py-1 rounded-full"
                        style={{ backgroundColor: c.priorityBg, color: c.priorityColor }}
                      >
                        {c.priority}
                      </span>
                    </td>
                    <td className="py-4 pr-4">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: c.statusDot }} />
                        <span className="text-sm text-gray-700">{c.status}</span>
                      </div>
                    </td>
                    <td className="py-4 pr-4">
                      <div className="flex items-center gap-1">
                        <div className="flex -space-x-2">
                          {c.avatars.map((src, i) => (
                            <img key={i} src={src} alt="" className="w-7 h-7 rounded-full border-2 border-white object-cover" />
                          ))}
                        </div>
                        <span className="text-xs text-gray-400 ml-1">{c.extra}</span>
                      </div>
                    </td>
                    <td className="py-4">
                      <button className="text-gray-400 hover:text-gray-600">
                        <MoreHorizontal size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </div>
  )
}
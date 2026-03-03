import { useState } from 'react'
import {
  Lightbulb, Paintbrush, Leaf, MoreHorizontal,
  Search, Plus, Minus, Crosshair, Layers,
  BarChart2, CheckCircle, AlertTriangle, Download
} from 'lucide-react'

const NAV_LINKS = ['Dashboard', 'Hotspot Map', 'Issues', 'Reports']

const CATEGORIES = [
  { label: 'LIGHTING',  icon: Lightbulb },
  { label: 'GRAFFITI',  icon: Paintbrush },
  { label: 'WASTE',     icon: Leaf },
  { label: 'OTHERS',    icon: MoreHorizontal },
]

const LEGEND = [
  { color: '#ef4444', label: 'Critical Issue' },
  { color: '#f97316', label: 'Maintenance' },
  { color: '#22c55e', label: 'Operational' },
]

// Hotspot blobs on the map
const HOTSPOTS = [
  { id: 1, x: '42%', y: '32%', size: 180, color: 'rgba(205,100,70,0.25)', icon: '📍', iconBg: '#fff', iconColor: '#e05535', type: 'pin' },
  { id: 2, x: '68%', y: '52%', size: 140, color: 'rgba(205,100,70,0.18)', icon: '🖌',  iconBg: '#fff', iconColor: '#b85c2a', type: 'graffiti' },
  { id: 3, x: '55%', y: '68%', size: 200, color: 'rgba(205,100,70,0.22)', icon: '⚠',  iconBg: '#fff', iconColor: '#e05535', type: 'alert' },
]

export default function HotspotMap() {
  const [activeNav, setActiveNav] = useState('Hotspot Map')
  const [resolved, setResolved] = useState(false)
  const [activeCategories, setActiveCategories] = useState(['LIGHTING', 'GRAFFITI', 'WASTE', 'OTHERS'])

  const toggleCategory = (label) => {
    setActiveCategories(prev =>
      prev.includes(label) ? prev.filter(c => c !== label) : [...prev, label]
    )
  }

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8', fontFamily: 'sans-serif' }}>

      {/* ── TOP NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-6 shrink-0 bg-white shadow-sm z-10">
        {/* Logo */}
        <div className="flex items-center gap-2 w-48">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#ede8dc' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#b85c2a" />
              <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#b85c2a" />
              <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#b85c2a" />
              <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#b85c2a" />
            </svg>
          </div>
          <span className="font-extrabold text-base" style={{ color: '#1a1a1a' }}>Streetlight</span>
        </div>

        {/* Nav links */}
        <nav className="flex items-center gap-8">
          {NAV_LINKS.map(link => (
            <button
              key={link}
              onClick={() => setActiveNav(link)}
              className="text-sm font-medium pb-1 transition-colors"
              style={{
                color: activeNav === link ? '#b85c2a' : '#6b7280',
                borderBottom: activeNav === link ? '2px solid #b85c2a' : '2px solid transparent',
              }}
            >
              {link}
            </button>
          ))}
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-3 w-48 justify-end">
          <button className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#2d2d2d', color: '#fff', fontSize: 14 }}>
            🌙
          </button>
          <div className="text-right">
            <div className="text-sm font-bold text-gray-900 leading-tight">Alex Johnson</div>
            <div className="text-xs text-gray-400">Official Manager</div>
          </div>
          <div className="w-9 h-9 rounded-full overflow-hidden bg-gray-300 flex items-center justify-center text-sm font-bold text-white" style={{ backgroundColor: '#b85c2a' }}>
            AJ
          </div>
        </div>
      </header>

      {/* ── BODY ── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── LEFT SIDEBAR ── */}
        <aside className="w-72 shrink-0 flex flex-col overflow-y-auto p-5 gap-4 z-10" style={{ backgroundColor: '#f7f6e8' }}>

          {/* Title */}
          <div>
            <h1 className="text-xl font-extrabold text-gray-900">City Insights</h1>
            <p className="text-xs text-gray-400 mt-0.5">Map Variant 5/10 • Real-time Data</p>
          </div>

          {/* Search */}
          <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2.5 shadow-sm">
            <Search size={14} className="text-gray-400" />
            <input
              type="text"
              placeholder="Search locations..."
              className="flex-1 bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none"
            />
          </div>

          {/* Issue Severity */}
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-3">Issue Severity</p>
            <div className="flex flex-col gap-2.5">
              {/* High Priority */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-red-500 inline-block" />
                  <span className="text-sm text-gray-700">High Priority</span>
                </div>
                <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ backgroundColor: '#b85c2a' }}>
                  <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
              {/* In Progress */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-orange-400 inline-block" />
                  <span className="text-sm text-gray-700">In Progress</span>
                </div>
                <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ backgroundColor: '#b85c2a' }}>
                  <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
              {/* Resolved toggle */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
                  <span className="text-sm text-gray-700">Resolved</span>
                </div>
                <button
                  onClick={() => setResolved(!resolved)}
                  className="w-10 h-5 rounded-full transition-colors relative"
                  style={{ backgroundColor: resolved ? '#b85c2a' : '#d1d5db' }}
                >
                  <span
                    className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all"
                    style={{ left: resolved ? '22px' : '2px' }}
                  />
                </button>
              </div>
            </div>
          </div>

          {/* Category */}
          <div>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-3">Category</p>
            <div className="grid grid-cols-2 gap-2">
              {CATEGORIES.map(({ label, icon: Icon }) => (
                <button
                  key={label}
                  onClick={() => toggleCategory(label)}
                  className="flex flex-col items-center justify-center gap-1 py-3 rounded-2xl text-xs font-bold tracking-widest transition-all"
                  style={{
                    backgroundColor: activeCategories.includes(label) ? '#fff' : '#ede8dc',
                    color: '#b85c2a',
                    boxShadow: activeCategories.includes(label) ? '0 1px 4px rgba(0,0,0,0.08)' : 'none',
                  }}
                >
                  <Icon size={18} style={{ color: '#b85c2a' }} />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Impact Summary */}
          <div className="rounded-2xl p-4" style={{ backgroundColor: '#fff8f0', border: '1px solid #f0ddd0' }}>
            <p className="text-sm font-extrabold mb-2" style={{ color: '#b85c2a' }}>Impact Summary</p>
            <p className="text-xs text-gray-600 leading-relaxed mb-3">
              There are <strong>12 high priority</strong> cases requiring immediate attention in the Downtown District.
            </p>
            <button
              className="w-full py-2.5 rounded-xl text-white text-sm font-semibold flex items-center justify-center gap-2"
              style={{ backgroundColor: '#b85c2a' }}
            >
              Generate Report <Download size={14} />
            </button>
          </div>

          {/* Report New Issue */}
          <button
            className="w-full py-3 rounded-full text-white text-sm font-semibold flex items-center justify-center gap-2 mt-auto"
            style={{ backgroundColor: '#b85c2a' }}
          >
            <Plus size={16} /> Report New Issue
          </button>
        </aside>

        {/* ── MAP AREA ── */}
        <div className="flex-1 relative overflow-hidden" style={{ backgroundColor: '#e8c9a8' }}>

          {/* Map background gradient */}
          <div className="absolute inset-0" style={{
            background: 'radial-gradient(ellipse at 30% 40%, #e2b898 0%, #d4956a 40%, #c8815a 100%)'
          }} />

          {/* Diagonal light band */}
          <div className="absolute inset-0 opacity-30" style={{
            background: 'linear-gradient(135deg, rgba(255,220,180,0.6) 0%, transparent 50%, rgba(180,100,60,0.3) 100%)'
          }} />

          {/* Hotspot blobs */}
          {HOTSPOTS.map(h => (
            <div
              key={h.id}
              className="absolute flex items-center justify-center"
              style={{
                left: h.x,
                top: h.y,
                width: h.size,
                height: h.size * 0.6,
                transform: 'translate(-50%, -50%)',
                borderRadius: '50%',
                backgroundColor: h.color,
              }}
            >
              {/* Pin icon */}
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center shadow-md border-2 border-white"
                style={{ backgroundColor: h.iconBg }}
              >
                {h.type === 'pin' && (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="10" r="4" fill="#e05535"/>
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="#e05535"/>
                  </svg>
                )}
                {h.type === 'graffiti' && (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 000-1.41l-2.34-2.34a1 1 0 00-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="#b85c2a"/>
                  </svg>
                )}
                {h.type === 'alert' && (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" fill="#e05535"/>
                  </svg>
                )}
              </div>
            </div>
          ))}

          {/* Map Legend */}
          <div className="absolute bottom-28 left-6 bg-white rounded-2xl px-4 py-3 shadow-md">
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Map Legend</p>
            {LEGEND.map(l => (
              <div key={l.label} className="flex items-center gap-2 mb-1">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: l.color }} />
                <span className="text-xs text-gray-600">{l.label}</span>
              </div>
            ))}
          </div>

          {/* Bottom stats bar */}
          <div className="absolute bottom-5 left-1/2 -translate-x-1/2 bg-white rounded-2xl shadow-lg px-8 py-4 flex items-center gap-12" style={{ minWidth: 480 }}>
            {/* Live Impact */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#fff3eb' }}>
                <BarChart2 size={18} style={{ color: '#b85c2a' }} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold">Live Impact</p>
                <p className="text-lg font-extrabold text-gray-900">850 <span className="text-sm font-normal text-gray-400">/ 1000</span></p>
              </div>
            </div>

            <div className="w-px h-10 bg-gray-100" />

            {/* Fixed Today */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ backgroundColor: '#dcfce7' }}>
                <CheckCircle size={18} style={{ color: '#22c55e' }} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold">Fixed Today</p>
                <p className="text-lg font-extrabold text-gray-900">24 <span className="text-xs font-semibold text-green-500">+12%</span></p>
              </div>
            </div>

            <div className="w-px h-10 bg-gray-100" />

            {/* Unresolved */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#fff1f1' }}>
                <AlertTriangle size={18} style={{ color: '#ef4444' }} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold">Unresolved</p>
                <p className="text-lg font-extrabold text-gray-900">142</p>
              </div>
            </div>
          </div>

          {/* Map controls */}
          <div className="absolute top-5 right-5 flex flex-col gap-2">
            {[
              { icon: <Plus size={16} />, },
              { icon: <Minus size={16} />, },
              { icon: <Crosshair size={16} />, },
              { icon: <Layers size={16} />, },
            ].map((btn, i) => (
              <button
                key={i}
                className="w-10 h-10 bg-white rounded-xl shadow flex items-center justify-center text-gray-600 hover:bg-gray-50"
              >
                {btn.icon}
              </button>
            ))}
          </div>

        </div>
      </div>
    </div>
  )
}
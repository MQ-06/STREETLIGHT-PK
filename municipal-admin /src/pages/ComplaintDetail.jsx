import { useState } from 'react'
import { Bell, MapPin, ZoomIn, Download, Copy, ExternalLink } from 'lucide-react'

const NAV_LINKS = ['Dashboard', 'Complaints', 'Analytics', 'Map View']

const TIMELINE = [
  {
    id: 1,
    icon: '✓',
    iconBg: '#b85c2a',
    title: 'Report Submitted',
    date: 'Oct 24, 2023 • 09:15 AM',
    sub: 'Validated by City Network',
    note: null,
    active: true,
  },
  {
    id: 2,
    icon: '👤',
    iconBg: '#b85c2a',
    title: 'In Progress',
    titleDot: true,
    date: 'Oct 25, 2023 • 10:20 AM',
    sub: null,
    note: '"Team Alpha dispatched. Expected repair tonight."',
    active: true,
  },
  {
    id: 3,
    icon: '○',
    iconBg: '#d1d5db',
    title: 'Resolution Confirmed',
    date: 'Estimated: Oct 27',
    sub: null,
    note: null,
    active: false,
  },
]

const BLOCKCHAIN = [
  {
    label: 'Verification Hash',
    hash: '0x71C7656EC7ab88b098def8751B7401B5f6d8976F',
    time: '2 mins ago',
  },
  {
    label: 'Update Status Hash',
    hash: '0x4b20993bc2f98f65492d4b8e23924f2b3e8c89b1',
    time: 'Oct 25, 10:20 AM',
  },
]

export default function ComplaintDetail() {
  const [activeNav, setActiveNav] = useState('Complaints')

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── TOP NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-8 bg-white shadow-sm shrink-0">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#ede8dc' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#b85c2a" />
              <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#b85c2a" />
              <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#b85c2a" />
              <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#b85c2a" />
            </svg>
          </div>
          <span className="font-extrabold text-base tracking-widest uppercase" style={{ color: '#b85c2a' }}>
            Streetlight
          </span>
        </div>

        {/* Nav */}
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

        {/* Right */}
        <div className="flex items-center gap-3">
          <button className="w-9 h-9 rounded-full flex items-center justify-center bg-gray-100">
            <Bell size={16} className="text-gray-600" />
          </button>
          <div className="w-9 h-9 rounded-full bg-orange-300" />
        </div>
      </header>

      {/* ── CONTENT ── */}
      <div className="flex-1 px-8 py-6 flex gap-6 max-w-7xl mx-auto w-full">

        {/* ── LEFT COLUMN ── */}
        <div className="flex-1 flex flex-col gap-5">

          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span className="hover:text-gray-600 cursor-pointer">Complaints</span>
            <span>›</span>
            <span className="hover:text-gray-600 cursor-pointer">Downtown District</span>
            <span>›</span>
            <span className="font-semibold" style={{ color: '#b85c2a' }}>#SR-9921</span>
          </div>

          {/* Title */}
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900">Broken Streetlight – 5th Ave</h1>
            <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
              <MapPin size={13} />
              <span>1242 5th Avenue, Downtown District, Singapore</span>
            </div>
          </div>

          {/* Image */}
          <div className="relative rounded-2xl overflow-hidden" style={{ height: 320 }}>
            {/* High Priority badge */}
            <div className="absolute top-4 left-4 z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-white" style={{ backgroundColor: '#ef4444' }}>
              <span>!</span> HIGH PRIORITY
            </div>

            {/* Streetlight image from Unsplash */}
            <img
              src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"
              alt="Broken Streetlight"
              className="w-full h-full object-cover"
            />

            {/* Image action buttons */}
            <div className="absolute bottom-4 right-4 flex gap-2">
              <button className="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow">
                <ZoomIn size={15} className="text-gray-600" />
              </button>
              <button className="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow">
                <Download size={15} className="text-gray-600" />
              </button>
            </div>
          </div>

          {/* Citizen Description */}
          <div className="bg-white rounded-2xl p-5 shadow-sm">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#fff3eb' }}>
                <span style={{ fontSize: 14 }}>📄</span>
              </div>
              <span className="font-bold text-gray-800">Citizen Description</span>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed">
              "The street lamp outside our building has been flickering for three days and finally went out last night. It's making the sidewalk very dark and residents feel unsafe walking home late."
            </p>
          </div>

          {/* Blockchain Audit Trail */}
          <div className="bg-white rounded-2xl p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#eff6ff' }}>
                  <span style={{ fontSize: 14 }}>🔗</span>
                </div>
                <span className="font-bold text-gray-800">Blockchain Audit Trail</span>
              </div>
              <span className="text-xs font-semibold px-3 py-1 rounded-full" style={{ backgroundColor: '#eff6ff', color: '#3b82f6' }}>
                Polygon Mainnet
              </span>
            </div>

            <div className="flex flex-col gap-3">
              {BLOCKCHAIN.map((item, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl" style={{ backgroundColor: '#f9f9f9' }}>
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ backgroundColor: '#dcfce7' }}>
                      <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                        <path d="M2 6l3 3 5-5" stroke="#22c55e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-800">{item.label}</p>
                      <p className="text-xs text-gray-400 font-mono">{item.hash}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{item.time}</span>
                    <button className="text-gray-400 hover:text-gray-600">
                      <Copy size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* ── RIGHT COLUMN ── */}
        <div className="w-80 shrink-0 flex flex-col gap-4">

          {/* Action buttons */}
          <div className="flex gap-3">
            <button className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white shadow-sm text-sm font-semibold text-gray-700 hover:bg-gray-50 border border-gray-100">
              ✏️ Update Status
            </button>
            <button className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-semibold" style={{ backgroundColor: '#b85c2a' }}>
              👤 Assign Officer
            </button>
          </div>

          {/* AI Severity Score */}
          <div className="bg-white rounded-2xl p-5 shadow-sm text-center">
            <div className="flex items-center gap-2 mb-4">
              <span style={{ fontSize: 16 }}>🎯</span>
              <span className="font-bold text-gray-800">AI Severity Score</span>
            </div>

            {/* Circular progress */}
            <div className="flex items-center justify-center mb-3">
              <div className="relative w-28 h-28">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#f3f4f6" strokeWidth="8" />
                  <circle
                    cx="50" cy="50" r="40" fill="none"
                    stroke="#b85c2a" strokeWidth="8"
                    strokeDasharray="251"
                    strokeDashoffset="51"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-extrabold text-gray-900">7.4</span>
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">High Risk</span>
                </div>
              </div>
            </div>

            <p className="text-xs text-gray-500 leading-relaxed text-center">
              Based on lighting conditions, crime data, and traffic volume in this sector.
            </p>
          </div>

          {/* Status Timeline */}
          <div className="bg-white rounded-2xl p-5 shadow-sm">
            <h3 className="font-bold text-gray-800 mb-4">Status Timeline</h3>
            <div className="flex flex-col gap-0">
              {TIMELINE.map((item, i) => (
                <div key={item.id} className="flex gap-3">
                  {/* Icon + line */}
                  <div className="flex flex-col items-center">
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0"
                      style={{ backgroundColor: item.iconBg }}
                    >
                      {item.id === 1 ? (
                        <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                          <path d="M2 6l3 3 5-5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      ) : item.id === 2 ? (
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="white">
                          <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
                        </svg>
                      ) : (
                        <div className="w-3 h-3 rounded-full bg-gray-300" />
                      )}
                    </div>
                    {i < TIMELINE.length - 1 && (
                      <div className="w-0.5 flex-1 my-1" style={{ backgroundColor: item.active ? '#b85c2a' : '#e5e7eb', minHeight: 24 }} />
                    )}
                  </div>

                  {/* Content */}
                  <div className="pb-4 flex-1">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm font-bold ${item.active ? 'text-gray-900' : 'text-gray-400'}`}>
                        {item.title}
                      </p>
                      {item.titleDot && (
                        <span className="w-2 h-2 rounded-full bg-orange-400 inline-block" />
                      )}
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5">{item.date}</p>
                    {item.sub && <p className="text-xs text-gray-400">{item.sub}</p>}
                    {item.note && (
                      <div className="mt-2 p-2.5 rounded-xl text-xs text-gray-600 leading-relaxed" style={{ backgroundColor: '#fff8f0', border: '1px solid #f0ddd0' }}>
                        <span style={{ color: '#b85c2a', fontWeight: 700 }}>ℹ </span>
                        {item.note}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Location Context */}
          <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
            <div className="flex items-center justify-between px-5 py-3">
              <span className="font-bold text-gray-800">Location Context</span>
              <button className="text-gray-400 hover:text-gray-600">
                <ExternalLink size={14} />
              </button>
            </div>
            <div className="h-36 w-full overflow-hidden">
              <img
                src="https://maps.googleapis.com/maps/api/staticmap?center=1.3521,103.8198&zoom=15&size=320x144&maptype=roadmap&markers=color:orange%7C1.3521,103.8198&key=AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY"
                alt="Location Map"
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.onerror = null
                  e.target.src = 'https://images.unsplash.com/photo-1524661135-423995f22d0b?w=320&h=144&fit=crop&q=80'
                }}
              />
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
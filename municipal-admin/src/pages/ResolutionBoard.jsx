import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Search, Plus, MoreHorizontal, Clock, TrendingUp } from 'lucide-react'

const NAV_LINKS = [
  { label: 'DASHBOARD',         path: '/dashboard' },
  { label: 'RESOLUTION BOARD',  path: '/resolution-board' },
  { label: 'IMPACT ANALYTICS',  path: '/analytics' },
]

const COLUMNS = [
  {
    id: 'new',
    label: 'NEW REPORTS',
    count: '04',
    dot: '#3b82f6',
    cards: [
      {
        id: '#SR-9942',
        badge: 'HIGH PRIORITY',
        badgeBg: '#fef2f2',
        badgeColor: '#ef4444',
        title: 'Pothole on Market Street intersection',
        avatar: null,
        time: '2h ago',
        progress: null,
        quote: null,
        avatars: null,
      },
      {
        id: '#SR-9945',
        badge: 'MAINTENANCE',
        badgeBg: '#f0fdf4',
        badgeColor: '#22c55e',
        title: 'Broken Park Bench – Central Square',
        avatar: null,
        time: '4h ago',
        progress: null,
        quote: null,
        avatars: null,
      },
    ],
  },
  {
    id: 'pending',
    label: 'PENDING VERIFICATION',
    count: '02',
    dot: '#f97316',
    cards: [
      {
        id: '#SR-9938',
        badge: 'URGENT',
        badgeBg: '#fff7ed',
        badgeColor: '#f97316',
        title: 'Reported Gas Leak – North Sector',
        avatar: 'https://i.pravatar.cc/32?img=3',
        time: '5h ago',
        progress: null,
        quote: null,
        avatars: null,
        borderLeft: '#f97316',
      },
    ],
  },
  {
    id: 'inprogress',
    label: 'IN PROGRESS',
    count: '03',
    dot: '#ef4444',
    cards: [
      {
        id: '#SR-9921',
        badge: 'IN REPAIR',
        badgeBg: '#fff3eb',
        badgeColor: '#b85c2a',
        title: 'Broken Streetlight – 5th Ave',
        avatar: null,
        time: null,
        progress: 65,
        quote: '"Team Alpha dispatched. Expected repair tonight."',
        avatars: [
          'https://i.pravatar.cc/32?img=5',
          'https://i.pravatar.cc/32?img=6',
        ],
        highlighted: true,
      },
      {
        id: '#SR-9918',
        badge: 'CLEANING',
        badgeBg: '#eff6ff',
        badgeColor: '#3b82f6',
        title: 'Graffiti Removal – Riverside Dr.',
        avatar: 'https://i.pravatar.cc/32?img=7',
        time: '1d ago',
        progress: null,
        quote: null,
        avatars: null,
      },
    ],
  },
  {
    id: 'feedback',
    label: 'AWAITING FEEDBACK',
    count: '01',
    dot: '#a855f7',
    cards: [
      {
        id: '#SR-9910',
        badge: 'CITIZEN REVIEW',
        badgeBg: '#faf5ff',
        badgeColor: '#a855f7',
        title: 'Waste Bin Replacement – B...',
        avatar: 'https://i.pravatar.cc/32?img=8',
        time: null,
        progress: null,
        quote: null,
        avatars: null,
      },
    ],
  },
]

export default function ResolutionBoard() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-8 bg-white shadow-sm shrink-0">
        {/* Logo → dashboard */}
        <div className="flex items-center gap-3">
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
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-gray-100 text-gray-500 tracking-wide">
            ADMIN PORTAL
          </span>
        </div>

        {/* Nav */}
        <nav className="flex items-center gap-8">
          {NAV_LINKS.map(({ label, path }) => (
            <button
              key={label}
              onClick={() => navigate(path)}
              className="text-xs font-bold tracking-widest pb-1 transition-colors"
              style={{
                color: location.pathname === path ? '#b85c2a' : '#6b7280',
                borderBottom: location.pathname === path ? '2px solid #b85c2a' : '2px solid transparent',
              }}
            >
              {label}
            </button>
          ))}
        </nav>

        {/* Avatar → user-roles */}
        <div
          className="w-9 h-9 rounded-full overflow-hidden cursor-pointer"
          style={{ backgroundColor: '#b85c2a' }}
          onClick={() => navigate('/user-roles')}
        >
          <img src="https://i.pravatar.cc/36?img=1" alt="admin" className="w-full h-full object-cover" />
        </div>
      </header>

      {/* ── PAGE HEADER ── */}
      <div className="px-8 pt-6 pb-4 flex items-start justify-between shrink-0">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900">Complaint Resolution</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage and track municipal service requests across the Downtown District.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white rounded-full px-4 py-2.5 shadow-sm w-64">
            <Search size={14} className="text-gray-400" />
            <input
              type="text"
              placeholder="Search ID or Keyword..."
              className="flex-1 bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none"
            />
          </div>
          {/* New Report → complaint-management */}
          <button
            onClick={() => navigate('/complaint-management')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-full text-white text-sm font-semibold"
            style={{ backgroundColor: '#b85c2a' }}
          >
            <Plus size={15} /> New Report
          </button>
        </div>
      </div>

      {/* ── KANBAN BOARD ── */}
      <div className="flex-1 px-8 pb-8 overflow-auto">
        <div className="flex gap-4 min-w-max h-full">
          {COLUMNS.map(col => (
            <div key={col.id} className="w-72 flex flex-col gap-3">

              {/* Column header */}
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: col.dot }} />
                  <span className="text-xs font-bold tracking-widest text-gray-500">{col.label}</span>
                  <span
                    className="text-xs font-bold px-1.5 py-0.5 rounded-md"
                    style={{ backgroundColor: '#e5e7eb', color: '#6b7280' }}
                  >
                    {col.count}
                  </span>
                </div>
                <button className="text-gray-400 hover:text-gray-600">
                  <MoreHorizontal size={16} />
                </button>
              </div>

              {/* Cards — click → complaint-detail */}
              {col.cards.map(card => (
                <div
                  key={card.id}
                  className="bg-white rounded-2xl p-4 shadow-sm flex flex-col gap-2.5 cursor-pointer hover:shadow-md transition-shadow"
                  style={{
                    border: card.highlighted ? '2px solid #b85c2a' : '1px solid #f0ede6',
                    borderLeft: card.borderLeft ? `4px solid ${card.borderLeft}` : undefined,
                  }}
                  onClick={() => navigate('/complaint-detail')}
                >
                  {/* Top row: badge + SR id */}
                  <div className="flex items-center justify-between">
                    <span
                      className="text-xs font-bold px-2 py-0.5 rounded-full"
                      style={{ backgroundColor: card.badgeBg, color: card.badgeColor }}
                    >
                      {card.badge}
                    </span>
                    <div className="flex items-center gap-1">
                      <span className="text-xs text-gray-400">{card.id}</span>
                      {card.highlighted && (
                        <span style={{ color: '#b85c2a', fontSize: 14 }}>✦</span>
                      )}
                    </div>
                  </div>

                  {/* Title */}
                  <p className="text-sm font-bold text-gray-900 leading-snug">{card.title}</p>

                  {/* Quote */}
                  {card.quote && (
                    <p className="text-xs text-gray-500 italic leading-relaxed">{card.quote}</p>
                  )}

                  {/* Progress bar */}
                  {card.progress !== null && card.progress !== undefined && (
                    <div>
                      <div className="w-full h-1.5 rounded-full bg-gray-100 overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ width: `${card.progress}%`, backgroundColor: '#b85c2a' }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Bottom row */}
                  <div className="flex items-center justify-between mt-1">
                    <div className="flex items-center">
                      {card.avatars ? (
                        <div className="flex -space-x-2">
                          {card.avatars.map((src, i) => (
                            <img
                              key={i}
                              src={src}
                              alt="officer"
                              className="w-7 h-7 rounded-full border-2 border-white object-cover"
                            />
                          ))}
                        </div>
                      ) : card.avatar ? (
                        <img
                          src={card.avatar}
                          alt="officer"
                          className="w-7 h-7 rounded-full border-2 border-white object-cover"
                        />
                      ) : (
                        <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 text-xs font-bold">
                          ?
                        </div>
                      )}
                    </div>

                    {card.progress !== null && card.progress !== undefined ? (
                      <div className="flex items-center gap-1 text-xs font-semibold" style={{ color: '#b85c2a' }}>
                        <TrendingUp size={12} />
                        {card.progress}% done
                      </div>
                    ) : card.time ? (
                      <div className="flex items-center gap-1 text-xs text-gray-400">
                        <Clock size={11} />
                        {card.time}
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}

            </div>
          ))}
        </div>
      </div>

      {/* Dark mode button */}
      <div className="fixed bottom-6 left-6">
        <button className="w-11 h-11 rounded-full bg-white shadow-lg flex items-center justify-center text-lg">
          🌙
        </button>
      </div>

    </div>
  )
}
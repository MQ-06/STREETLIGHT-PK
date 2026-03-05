import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Bell, Download, Filter, Copy, TrendingUp, Clock, Link, AlignJustify, Eye, ChevronLeft, ChevronRight, Plus } from 'lucide-react'

const NAV_LINKS = [
  { label: 'Dashboard',    path: '/dashboard' },
  { label: 'Issues',       path: '/resolution-board' },
  { label: 'Transparency', path: '/transparency' },
  { label: 'Profile',      path: '/user-roles' },
]

const STATS = [
  { label: 'TOTAL LOGS',         value: '142,892', sub: '+1.2k today',       subIcon: 'trend'   },
  { label: 'ACTIVE VALIDATORS',  value: '12',      sub: 'Network Healthy',   subIcon: 'network' },
  { label: 'SYSTEM UPTIME',      value: '99.9%',   sub: 'Last block: 14s ago', subIcon: 'clock' },
  { label: 'BLOCK HEIGHT',       value: '#9.2M',   sub: 'v2.4.1-stable',     subIcon: 'version' },
]

const ACTION_COLORS = {
  STATUS_CHANGED:   { bg: '#e8f5e9', color: '#2e7d32' },
  NEW_REPORT_AUTH:  { bg: '#e3f2fd', color: '#1565c0' },
  IMG_METADATA_UPD: { bg: '#fff8e1', color: '#f57f17' },
  ISSUE_RESOLVED:   { bg: '#e8f5e9', color: '#2e7d32' },
  BLOCK_FINALIZED:  { bg: '#f3e5f5', color: '#6a1b9a' },
}

const NODE_COLORS = {
  'USR-9921-X':    '#ef4444',
  'SYS-AUTH-02':   '#3b82f6',
  'USR-1045-A':    '#ef4444',
  'USR-5520-K':    '#ef4444',
  'NODE-VLDTR-09': '#9ca3af',
}

const LOGS = [
  { date: 'Oct 25, 2023', time: '14:25:41 UTC', node: 'USR-9921-X',    action: 'STATUS_CHANGED',   hash: '0x7a2...4f9b' },
  { date: 'Oct 25, 2023', time: '13:58:12 UTC', node: 'SYS-AUTH-02',   action: 'NEW_REPORT_AUTH',  hash: '0x3b1...c45e' },
  { date: 'Oct 25, 2023', time: '11:15:04 UTC', node: 'USR-1045-A',    action: 'IMG_METADATA_UPD', hash: '0xde4...882a' },
  { date: 'Oct 24, 2023', time: '18:42:55 UTC', node: 'USR-5520-K',    action: 'ISSUE_RESOLVED',   hash: '0x992...31f0' },
  { date: 'Oct 24, 2023', time: '16:02:11 UTC', node: 'NODE-VLDTR-09', action: 'BLOCK_FINALIZED',  hash: '0x1c8...a49d' },
]

export default function Transparency() {
  const navigate = useNavigate()
  const location = useLocation()
  const [activePage, setActivePage] = useState(1)

  return (
    <div className="h-screen flex flex-col overflow-y-auto" style={{ backgroundColor: '#faf9f2' }}>

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
          <button className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
            <span className="text-sm">◑</span>
          </button>
          <div
            className="w-8 h-8 rounded-full overflow-hidden bg-orange-200 cursor-pointer"
            onClick={() => navigate('/user-roles')}
          >
            <img src="https://i.pravatar.cc/32?img=1" alt="user" className="w-full h-full object-cover" />
          </div>
        </div>
      </header>

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 px-8 py-6 flex flex-col gap-6">

        {/* Page header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span style={{ color: '#b85c2a', fontSize: 14 }}>🔗</span>
              <span className="text-xs font-bold tracking-widest uppercase" style={{ color: '#b85c2a' }}>
                Immutable Audit Trail
              </span>
            </div>
            <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
              Blockchain Transparency Logs
            </h1>
            <p className="text-sm text-gray-500 leading-relaxed max-w-lg">
              Every action on the Streetlight platform is recorded on a decentralized ledger. These
              logs ensure complete accountability and public trust in municipal operations.
            </p>
          </div>
          <div className="flex items-center gap-3 mt-2">
            <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white border border-gray-200 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50">
              <Filter size={14} /> Filters
            </button>
            <button
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-sm font-semibold shadow-sm"
              style={{ backgroundColor: '#b85c2a' }}
            >
              <Download size={14} /> Export CSV
            </button>
          </div>
        </div>

        {/* ── STAT CARDS — click → analytics ── */}
        <div className="grid grid-cols-4 gap-4">
          {STATS.map((s) => (
            <div
              key={s.label}
              className="rounded-2xl p-5 flex flex-col gap-2 cursor-pointer hover:opacity-80 transition-opacity"
              style={{ backgroundColor: '#f0ede3', border: '1px solid #e8e3d8' }}
              onClick={() => navigate('/analytics')}
            >
              <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">{s.label}</p>
              <p className="text-3xl font-extrabold text-gray-900">{s.value}</p>
              <div className="flex items-center gap-1">
                {s.subIcon === 'trend'   && <TrendingUp size={12} style={{ color: '#22c55e' }} />}
                {s.subIcon === 'network' && <span className="text-xs" style={{ color: '#b85c2a' }}>∞</span>}
                {s.subIcon === 'clock'   && <Clock size={12} className="text-gray-400" />}
                {s.subIcon === 'version' && <span className="text-xs text-gray-400">v</span>}
                <span className="text-xs text-gray-500">{s.sub}</span>
              </div>
            </div>
          ))}
        </div>

        {/* ── LOGS TABLE ── */}
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden border border-gray-100">
          <table className="w-full">
            <thead>
              <tr style={{ backgroundColor: '#faf9f2', borderBottom: '1px solid #f0ede3' }}>
                {['TIMESTAMP', 'USER ID / NODE', 'ACTION', 'TRANSACTION HASH', 'DETAILS'].map(h => (
                  <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-6 py-4">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {LOGS.map((log, i) => (
                <tr
                  key={i}
                  className="border-b last:border-0 hover:bg-gray-50 transition-colors cursor-pointer"
                  style={{ borderColor: '#f5f5f5' }}
                  onClick={() => navigate('/complaint-detail')}
                >
                  {/* Timestamp */}
                  <td className="px-6 py-5">
                    <p className="text-sm font-semibold text-gray-800">{log.date}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{log.time}</p>
                  </td>

                  {/* Node */}
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: NODE_COLORS[log.node] || '#9ca3af' }} />
                      <span className="text-sm font-mono text-gray-700">{log.node}</span>
                    </div>
                  </td>

                  {/* Action badge */}
                  <td className="px-6 py-5">
                    <span
                      className="text-xs font-bold px-3 py-1.5 rounded-lg font-mono tracking-wide"
                      style={{
                        backgroundColor: ACTION_COLORS[log.action]?.bg || '#f3f4f6',
                        color: ACTION_COLORS[log.action]?.color || '#6b7280',
                      }}
                    >
                      {log.action}
                    </span>
                  </td>

                  {/* Hash */}
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono text-gray-600">{log.hash}</span>
                      <button
                        className="text-gray-300 hover:text-gray-500 transition-colors"
                        onClick={e => e.stopPropagation()}
                      >
                        <Copy size={13} />
                      </button>
                    </div>
                  </td>

                  {/* Verify → complaint-detail */}
                  <td className="px-6 py-5">
                    <button
                      className="text-sm font-bold hover:opacity-70 transition-opacity"
                      style={{ color: '#b85c2a' }}
                      onClick={e => { e.stopPropagation(); navigate('/complaint-detail') }}
                    >
                      Verify
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div
            className="flex items-center justify-between px-6 py-4"
            style={{ borderTop: '1px solid #f0ede3', backgroundColor: '#faf9f2' }}
          >
            <p className="text-sm text-gray-500">
              Showing <span className="font-bold text-gray-800">1-10</span> of{' '}
              <span className="font-bold text-gray-800">142,892</span> logs
            </p>
            <div className="flex items-center gap-1">
              <button className="w-8 h-8 rounded-lg flex items-center justify-center bg-white border border-gray-200 text-gray-400 hover:bg-gray-50">
                <ChevronLeft size={14} />
              </button>
              {[1, 2, 3].map((p) => (
                <button
                  key={p}
                  onClick={() => setActivePage(p)}
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold transition-all"
                  style={{
                    backgroundColor: activePage === p ? '#b85c2a' : '#fff',
                    color: activePage === p ? '#fff' : '#6b7280',
                    border: activePage === p ? 'none' : '1px solid #e5e7eb',
                  }}
                >
                  {p}
                </button>
              ))}
              <button className="w-8 h-8 rounded-lg flex items-center justify-center bg-white border border-gray-200 text-gray-400 hover:bg-gray-50">
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        </div>

        {/* ── HOW IT WORKS ── */}
        <div
          className="rounded-2xl p-6 flex items-center justify-between"
          style={{ border: '1.5px dashed #d4b896', backgroundColor: '#fdf9f5' }}
        >
          <div className="max-w-md">
            <h3 className="text-base font-extrabold text-gray-900 mb-2">How it works</h3>
            <p className="text-sm text-gray-500 leading-relaxed">
              Streetlight uses a private blockchain network to ensure that municipal data remains
              untampered. Once a citizen submits a report or a technician updates a status, the transaction
              is hashed and distributed across validator nodes, creating a permanent, verifiable record for
              all stakeholders.
            </p>
          </div>
          <div className="flex items-center gap-3">
            {[
              { icon: Link,         label: 'HASH ID'    },
              { icon: AlignJustify, label: 'IMMUTABLE'  },
              { icon: Eye,          label: 'AUDITABLE'  },
            ].map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex flex-col items-center justify-center gap-2 w-28 h-24 rounded-2xl cursor-pointer hover:opacity-80"
                style={{ backgroundColor: '#f0ede3' }}
                onClick={() => navigate('/analytics')}
              >
                <Icon size={22} style={{ color: '#b85c2a' }} />
                <span className="text-xs font-bold tracking-widest text-gray-500">{label}</span>
              </div>
            ))}
          </div>
        </div>

      </main>

      {/* ── FOOTER ── */}
      <footer className="py-10 text-center border-t border-gray-100 mt-4">
        <div
          className="flex items-center justify-center gap-2 mb-3 cursor-pointer"
          onClick={() => navigate('/dashboard')}
        >
          <div className="w-7 h-7 rounded-md flex items-center justify-center" style={{ backgroundColor: '#ede8dc' }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
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
        <p className="text-xs text-gray-400 mb-4">
          © 2023 Municipal Digital Services. Powered by Civic-Chain Technology.
        </p>
        <div className="flex items-center justify-center gap-8 text-xs text-gray-400">
          <a href="#" className="hover:text-gray-600">Terms of Service</a>
          <a href="#" className="hover:text-gray-600">Privacy Policy</a>
          <a href="#" className="hover:text-gray-600">Network Status</a>
        </div>
      </footer>

      {/* Floating NEW REPORT → complaint-management */}
      <div className="fixed bottom-8 right-8">
        <button
          onClick={() => navigate('/complaint-management')}
          className="flex items-center gap-2 px-5 py-3 rounded-full text-white text-sm font-bold shadow-lg"
          style={{ backgroundColor: '#b85c2a' }}
        >
          <Plus size={16} /> NEW REPORT
        </button>
      </div>

    </div>
  )
}
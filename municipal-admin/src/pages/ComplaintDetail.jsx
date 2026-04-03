import { useState, useEffect } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import { Bell, MapPin, ZoomIn, Download, Copy, ExternalLink } from 'lucide-react'
import { authFetch } from '../utils/auth'

const NAV_LINKS = [
  { label: 'Dashboard',   path: '/dashboard' },
  { label: 'Complaints',  path: '/complaint-management' },
  { label: 'Analytics',   path: '/analytics' },
  { label: 'Map View',    path: '/hotspot-map' },
]

export default function ComplaintDetail() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const { id }    = useParams()

  const [report,  setReport]  = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    if (!id) { setLoading(false); return }
    authFetch(`/admin/reports/${id}`)
      .then(r => r.json())
      .then(data => { setReport(data); setLoading(false) })
      .catch(() => { setError('Failed to load report.'); setLoading(false) })
  }, [id])

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ backgroundColor: '#f7f6e8' }}>
        <p className="text-gray-400 text-sm">Loading report…</p>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4" style={{ backgroundColor: '#f7f6e8' }}>
        <p className="text-red-500 text-sm">{error || 'Report not found.'}</p>
        <button onClick={() => navigate('/complaint-management')} className="text-sm underline" style={{ color: '#b85c2a' }}>
          Back to Complaints
        </button>
      </div>
    )
  }

  const aiScore      = Math.round((report.ai_confidence ?? 0))
  const scoreDash    = Math.round(251 - (aiScore / 100) * 251)

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* ── TOP NAVBAR ── */}
      <header className="h-14 flex items-center justify-between px-8 bg-white shadow-sm shrink-0">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
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

        <nav className="flex items-center gap-8">
          {NAV_LINKS.map(({ label, path }) => (
            <button
              key={label}
              onClick={() => navigate(path)}
              className="text-sm font-medium pb-1 transition-colors"
              style={{
                color:        location.pathname.startsWith(path) ? '#b85c2a' : '#6b7280',
                borderBottom: location.pathname.startsWith(path) ? '2px solid #b85c2a' : '2px solid transparent',
              }}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/complaint-management')} className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center">
            <Bell size={16} className="text-gray-600" />
          </button>
        </div>
      </header>

      {/* ── CONTENT ── */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        <div className="flex gap-6 max-w-7xl mx-auto w-full">

          {/* ── LEFT COLUMN ── */}
          <div className="flex-1 flex flex-col gap-5">

            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <span className="hover:text-gray-600 cursor-pointer" onClick={() => navigate('/complaint-management')}>
                Complaints
              </span>
              <span>›</span>
              <span className="font-semibold" style={{ color: '#b85c2a' }}>{report.display_id}</span>
            </div>

            {/* Title */}
            <div>
              <h1 className="text-2xl font-extrabold text-gray-900">{report.title}</h1>
              <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
                <MapPin size={13} />
                <span>{report.location}</span>
              </div>
            </div>

            {/* Image */}
            {report.image_url && (
              <div className="relative rounded-2xl overflow-hidden" style={{ height: 320 }}>
                <div
                  className="absolute top-4 left-4 z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-white"
                  style={{ backgroundColor: report.severity_color || '#ef4444' }}
                >
                  {report.severity?.toUpperCase()} SEVERITY
                </div>
                <img src={report.image_url} alt={report.title} className="w-full h-full object-cover" />
                <div className="absolute bottom-4 right-4 flex gap-2">
                  <a href={report.image_url} target="_blank" rel="noreferrer"
                    className="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow">
                    <ZoomIn size={15} className="text-gray-600" />
                  </a>
                </div>
              </div>
            )}

            {/* Description */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#fff3eb' }}>
                  <span style={{ fontSize: 14 }}>📄</span>
                </div>
                <span className="font-bold text-gray-800">Citizen Description</span>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">
                {report.description || 'No description provided.'}
              </p>
              <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-4 text-xs text-gray-400">
                <span>Reported by: <span className="font-semibold text-gray-600">{report.reporter_name}</span></span>
                <span>AI Class: <span className="font-semibold text-gray-600">{report.category}</span></span>
                {report.assigned_department && (
                  <span>Dept: <span className="font-semibold text-gray-600 uppercase">{report.assigned_department}</span></span>
                )}
              </div>
            </div>

            {/* Audit Log */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#eff6ff' }}>
                  <span style={{ fontSize: 14 }}>📋</span>
                </div>
                <span className="font-bold text-gray-800">Audit Log</span>
              </div>
              {(report.logs || []).length === 0 ? (
                <p className="text-sm text-gray-400">No log entries yet.</p>
              ) : (
                <div className="flex flex-col gap-2">
                  {(report.logs || []).map((log, i) => (
                    <div key={i} className="flex items-start justify-between p-3 rounded-xl" style={{ backgroundColor: '#f9f9f9' }}>
                      <div className="flex items-start gap-3">
                        <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                          style={{ backgroundColor: log.ai_managed ? '#eff6ff' : '#fff3eb' }}>
                          <span style={{ fontSize: 10 }}>{log.ai_managed ? '🤖' : '👤'}</span>
                        </div>
                        <div>
                          {log.new_stage && (
                            <p className="text-xs font-semibold text-gray-800">
                              {log.previous_stage ?? '—'} → {log.new_stage}
                            </p>
                          )}
                          <p className="text-xs text-gray-500 mt-0.5">{log.note}</p>
                        </div>
                      </div>
                      <span className="text-xs text-gray-400 shrink-0 ml-3">
                        {log.created_at ? new Date(log.created_at).toLocaleString() : ''}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* ── RIGHT COLUMN ── */}
          <div className="w-80 shrink-0 flex flex-col gap-4">

            {/* Action buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/resolution-board')}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white shadow-sm text-sm font-semibold text-gray-700 hover:bg-gray-50 border border-gray-100"
              >
                ✏️ Update Status
              </button>
              <button
                onClick={() => navigate('/resolution-board')}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-semibold"
                style={{ backgroundColor: '#b85c2a' }}
              >
                📋 View Board
              </button>
            </div>

            {/* AI Confidence Score */}
            <div className="bg-white rounded-2xl p-5 shadow-sm text-center">
              <div className="flex items-center gap-2 mb-4">
                <span style={{ fontSize: 16 }}>🎯</span>
                <span className="font-bold text-gray-800">AI Confidence</span>
              </div>
              <div className="flex items-center justify-center mb-3">
                <div className="relative w-28 h-28">
                  <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                    <circle cx="50" cy="50" r="40" fill="none" stroke="#f3f4f6" strokeWidth="8" />
                    <circle
                      cx="50" cy="50" r="40" fill="none"
                      stroke="#b85c2a" strokeWidth="8"
                      strokeDasharray="251"
                      strokeDashoffset={scoreDash}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-extrabold text-gray-900">{aiScore}</span>
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">/ 100</span>
                  </div>
                </div>
              </div>
              <div className="text-xs text-gray-500 space-y-1">
                {report.combined_score != null && (
                  <p>Combined score: <span className="font-semibold">{Math.round(report.combined_score)}</span></p>
                )}
                {report.trust_score != null && (
                  <p>Trust score: <span className="font-semibold">{Math.round(report.trust_score)}</span></p>
                )}
                <p>GPS verified: <span className="font-semibold">{report.gps_verified ? 'Yes' : 'No'}</span></p>
              </div>
            </div>

            {/* Stage info */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <h3 className="font-bold text-gray-800 mb-3">Current Stage</h3>
              <div className="flex items-center gap-2 mb-2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: report.stage_dot }} />
                <span className="text-sm font-semibold text-gray-800">
                  {(report.kanban_stage || 'NEW').replace(/_/g, ' ')}
                </span>
              </div>
              {report.assigned_city && (
                <p className="text-xs text-gray-500 capitalize">City: {report.assigned_city}</p>
              )}
              {report.assigned_department && (
                <p className="text-xs text-gray-500 uppercase">Dept: {report.assigned_department}</p>
              )}
              {report.assigned_at && (
                <p className="text-xs text-gray-400 mt-1">
                  Routed: {new Date(report.assigned_at).toLocaleString()}
                </p>
              )}
              {report.is_flagged_for_spam && (
                <p className="text-xs text-red-500 font-semibold mt-2">⚠ Flagged for spam review</p>
              )}
            </div>

            {/* Location */}
            {report.lat && report.lng && (
              <div className="bg-white rounded-2xl overflow-hidden shadow-sm">
                <div className="flex items-center justify-between px-5 py-3">
                  <span className="font-bold text-gray-800">Location</span>
                  <button onClick={() => navigate('/hotspot-map')} className="text-gray-400 hover:text-gray-600">
                    <ExternalLink size={14} />
                  </button>
                </div>
                <div className="px-5 pb-4 text-xs text-gray-500">
                  <p>{report.lat.toFixed(5)}, {report.lng.toFixed(5)}</p>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  )
}
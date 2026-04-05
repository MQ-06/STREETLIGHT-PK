import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { MapPin, ZoomIn, ExternalLink, FileText, ClipboardList, Target, Pencil, Layers, AlertTriangle, Bot, User, Send } from 'lucide-react'
import { authFetch } from '../../utils/auth'
import StageBadge from '../../components/StageBadge'

export default function ComplaintDetail() {
  const navigate        = useNavigate()
  const { id }          = useParams()
  const [report,  setReport]  = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const [note,        setNote]        = useState('')
  const [noteLoading, setNoteLoading] = useState(false)
  const [noteError,   setNoteError]   = useState('')

  function loadReport() {
    if (!id) { setLoading(false); return }
    authFetch('/admin/reports/' + id)
      .then(r => r.json())
      .then(d => { setReport(d); setLoading(false) })
      .catch(() => { setError('Failed to load report.'); setLoading(false) })
  }

  useEffect(() => { loadReport() }, [id])

  async function handleAddNote(e) {
    e.preventDefault()
    if (!note.trim()) return
    setNoteLoading(true)
    setNoteError('')
    try {
      const res = await authFetch('/admin/reports/' + id + '/note', {
        method: 'POST',
        body:   JSON.stringify({ note: note.trim() }),
      })
      if (!res.ok) {
        const d = await res.json().catch(() => ({}))
        setNoteError(d.detail || 'Failed to add note.')
        setNoteLoading(false)
        return
      }
      setNote('')
      loadReport()
    } catch {
      setNoteError('Network error.')
    }
    setNoteLoading(false)
  }

  if (loading) return <div className="p-6 text-center text-sm text-gray-400">Loading report…</div>
  if (error || !report) return (
    <div className="p-6 flex flex-col items-center gap-4">
      <p className="text-red-500 text-sm">{error || 'Report not found.'}</p>
      <button onClick={() => navigate('/complaint-management')} className="text-sm underline text-primary">Back to Complaints</button>
    </div>
  )

  const aiScore   = Math.round(report.ai_confidence ?? 0)
  const scoreDash = Math.round(251 - (aiScore / 100) * 251)

  return (
    <div className="p-6">
      <div className="flex gap-6 max-w-7xl w-full">
        {/* Left */}
        <div className="flex-1 flex flex-col gap-5">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span className="hover:text-gray-600 cursor-pointer" onClick={() => navigate('/complaint-management')}>Complaints</span>
            <span>›</span>
            <span className="font-semibold text-primary">{report.display_id}</span>
          </div>

          <div>
            <h1 className="text-2xl font-black text-gray-900">{report.title}</h1>
            <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
              <MapPin size={13} /><span>{report.location}</span>
            </div>
          </div>

          {report.image_url && (
            <div className="relative rounded-2xl overflow-hidden" style={{ height: 320 }}>
              <div className="absolute top-4 left-4 z-10 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-white"
                style={{ backgroundColor: report.severity_color || '#ef4444' }}>
                {(report.severity || '').toUpperCase()} SEVERITY
              </div>
              <img src={report.image_url} alt={report.title} className="w-full h-full object-cover" />
              <a href={report.image_url} target="_blank" rel="noreferrer"
                className="absolute bottom-4 right-4 w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow">
                <ZoomIn size={15} className="text-gray-600" />
              </a>
            </div>
          )}

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-warm-border">
            <div className="flex items-center gap-2 mb-3">
              <FileText size={16} className="text-gray-500" />
              <span className="font-bold text-gray-800">Citizen Description</span>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed">{report.description || 'No description provided.'}</p>
            <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-4 text-xs text-gray-400">
              <span>Reporter: <span className="font-semibold text-gray-600">{report.reporter_name}</span></span>
              <span>Category: <span className="font-semibold text-gray-600">{report.category}</span></span>
              {report.assigned_department && <span>Dept: <span className="font-semibold uppercase">{report.assigned_department}</span></span>}
            </div>
          </div>

          {/* Notes / Add note */}
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-warm-border">
            <div className="flex items-center gap-2 mb-4">
              <ClipboardList size={16} className="text-gray-500" />
              <span className="font-bold text-gray-800">Internal Notes</span>
            </div>
            <form onSubmit={handleAddNote} className="flex gap-2 mb-4">
              <input
                type="text"
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="Add an internal note or comment…"
                className="flex-1 text-sm px-3 py-2.5 rounded-xl border border-warm-border outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
              />
              <button
                type="submit"
                disabled={noteLoading || !note.trim()}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-white text-sm font-semibold hover:bg-primary-dark disabled:opacity-50 shrink-0"
              >
                <Send size={13} />
                {noteLoading ? '…' : 'Post'}
              </button>
            </form>
            {noteError && <p className="text-xs text-red-500 mb-3">{noteError}</p>}

            {/* Note entries from audit log (notes only — no stage transitions) */}
            {(report.logs || []).filter(l => l.note && !l.new_stage).length === 0 ? (
              <p className="text-sm text-gray-400">No notes yet.</p>
            ) : (report.logs || []).filter(l => l.note && !l.new_stage).map((log, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-xl mb-2 last:mb-0" style={{ backgroundColor: '#F9F9F9' }}>
                <div className="mt-0.5 w-6 h-6 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: log.ai_managed ? '#F0FDF4' : '#FFF3EB' }}>
                  {log.ai_managed ? <Bot size={12} className="text-green-600" /> : <User size={12} className="text-primary" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-700">{log.note}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{log.created_at ? new Date(log.created_at).toLocaleString() : ''}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-warm-border">
            <div className="flex items-center gap-2 mb-4">
              <Layers size={16} className="text-gray-500" />
              <span className="font-bold text-gray-800">Audit Log</span>
            </div>
            {(report.logs || []).length === 0 ? (
              <p className="text-sm text-gray-400">No log entries yet.</p>
            ) : (report.logs || []).map((log, i) => (
              <div key={i} className="flex items-start justify-between p-3 rounded-xl mb-2 last:mb-0" style={{ backgroundColor: '#F9F9F9' }}>
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 w-6 h-6 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: log.ai_managed ? '#F0FDF4' : '#FFF3EB' }}>
                    {log.ai_managed ? <Bot size={12} className="text-green-600" /> : <User size={12} className="text-primary" />}
                  </div>
                  <div>
                    {log.new_stage && (
                      <p className="text-xs font-semibold text-gray-800">{log.previous_stage ?? '—'} → {log.new_stage}</p>
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
        </div>

        {/* Right */}
        <div className="w-80 shrink-0 flex flex-col gap-4">
          <div className="flex gap-3">
            <button onClick={() => navigate('/resolution-board')} className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white shadow-sm text-sm font-semibold text-gray-700 hover:bg-gray-50 border border-warm-border">
              <Pencil size={14} /> Update Status
            </button>
            <button onClick={() => navigate('/resolution-board')} className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark">
              <Layers size={14} /> View Board
            </button>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-warm-border text-center">
            <div className="flex items-center gap-2 mb-4">
              <Target size={16} className="text-gray-500" />
              <span className="font-bold text-gray-800">AI Confidence</span>
            </div>
            <div className="flex items-center justify-center mb-3">
              <div className="relative w-28 h-28">
                <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#F3F4F6" strokeWidth="8" />
                  <circle cx="50" cy="50" r="40" fill="none" stroke="#B85C2E" strokeWidth="8"
                    strokeDasharray="251" strokeDashoffset={scoreDash} strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-black text-gray-900">{aiScore}</span>
                  <span className="text-xs font-bold text-gray-400 uppercase tracking-wide">/ 100</span>
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              {report.combined_score != null && <p>Combined: <span className="font-semibold">{Math.round(report.combined_score)}</span></p>}
              {report.trust_score    != null && <p>Trust: <span className="font-semibold">{Math.round(report.trust_score)}</span></p>}
              <p>GPS verified: <span className="font-semibold">{report.gps_verified ? 'Yes' : 'No'}</span></p>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-warm-border">
            <h3 className="font-bold text-gray-800 mb-3">Current Stage</h3>
            <StageBadge stage={report.kanban_stage || 'NEW'} />
            {report.assigned_city       && <p className="text-xs text-gray-500 mt-2 capitalize">City: {report.assigned_city}</p>}
            {report.assigned_department && <p className="text-xs text-gray-500 uppercase">Dept: {report.assigned_department}</p>}
            {report.assigned_at         && <p className="text-xs text-gray-400 mt-1">Routed: {new Date(report.assigned_at).toLocaleString()}</p>}
            {report.is_flagged_for_spam && (
              <div className="flex items-center gap-1.5 mt-2">
                <AlertTriangle size={13} className="text-red-500" />
                <p className="text-xs text-red-500 font-semibold">Flagged for spam review</p>
              </div>
            )}
          </div>

          {report.lat && report.lng && (
            <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-warm-border">
              <div className="flex items-center justify-between px-5 py-3">
                <span className="font-bold text-gray-800">Location</span>
                <button onClick={() => navigate('/hotspot-map')} className="text-gray-400 hover:text-gray-600"><ExternalLink size={14} /></button>
              </div>
              <p className="px-5 pb-4 text-xs text-gray-500">{report.lat.toFixed(5)}, {report.lng.toFixed(5)}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { RefreshCw, Bot, User, ChevronRight } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch } from '../../utils/auth'

const PAGE_SIZE = 50

export default function AuditLog() {
  const navigate = useNavigate()
  const [logs,    setLogs]    = useState([])
  const [total,   setTotal]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [page,    setPage]    = useState(1)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const skip = (page - 1) * PAGE_SIZE
      const res  = await authFetch(`/admin/audit-logs?skip=${skip}&limit=${PAGE_SIZE}`)
      const data = await res.json()
      setLogs(data.logs  || [])
      setTotal(data.total || 0)
    } catch {
      // silently fail
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => { load() }, [load])

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="p-6 flex flex-col gap-5">
      <PageHeader title="Audit Log" subtitle="Immutable trail of every status change and action across all reports.">
        <button
          onClick={load}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </PageHeader>

      <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-50 bg-gray-50/50">
              {['Time', 'Report', 'Actor', 'Transition', 'Note', ''].map(h => (
                <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-5 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [1, 2, 3, 4, 5].map(i => (
                <tr key={i}>
                  <td colSpan={6} className="px-5 py-3">
                    <div className="h-8 bg-gray-100 animate-pulse rounded-xl" />
                  </td>
                </tr>
              ))
            ) : logs.length === 0 ? (
              <tr><td colSpan={6} className="px-5 py-10 text-center text-sm text-gray-400">No audit entries found.</td></tr>
            ) : logs.map(log => (
              <tr key={log.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="px-5 py-3 text-xs text-gray-400 whitespace-nowrap">
                  {log.created_at ? new Date(log.created_at).toLocaleString() : '—'}
                </td>
                <td className="px-5 py-3">
                  <button
                    onClick={() => navigate('/complaint-detail/' + log.report_id)}
                    className="text-sm font-bold text-primary hover:underline"
                  >
                    {log.display_id}
                  </button>
                </td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-1.5">
                    <div className="w-5 h-5 rounded-full flex items-center justify-center shrink-0"
                      style={{ backgroundColor: log.ai_managed ? '#F0FDF4' : '#FFF3EB' }}>
                      {log.ai_managed
                        ? <Bot size={11} className="text-green-600" />
                        : <User size={11} className="text-primary" />}
                    </div>
                    <span className="text-xs font-semibold text-gray-700">
                      {log.ai_managed ? 'AI Agent' : `User #${log.changed_by}`}
                    </span>
                  </div>
                </td>
                <td className="px-5 py-3">
                  {log.new_stage ? (
                    <div className="flex items-center gap-1 text-xs font-semibold">
                      <span className="text-gray-500">{log.previous_stage ?? '—'}</span>
                      <ChevronRight size={12} className="text-gray-400" />
                      <span className="text-primary">{log.new_stage}</span>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400 italic">note</span>
                  )}
                </td>
                <td className="px-5 py-3 text-xs text-gray-500 max-w-xs truncate">{log.note || '—'}</td>
                <td className="px-5 py-3 text-xs text-gray-400 uppercase capitalize">
                  {log.assigned_city || ''}
                  {log.assigned_department ? ' · ' + log.assigned_department.toUpperCase() : ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="flex items-center justify-between px-5 py-4 border-t border-gray-50">
          <p className="text-sm text-gray-500">
            Showing <span className="font-bold text-gray-800">{Math.min((page - 1) * PAGE_SIZE + 1, total)}–{Math.min(page * PAGE_SIZE, total)}</span> of <span className="font-bold text-gray-800">{total}</span>
          </p>
          <div className="flex items-center gap-1.5">
            <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
              className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-40">Previous</button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
              <button key={p} onClick={() => setPage(p)}
                className="w-8 h-8 rounded-lg text-sm font-bold"
                style={{ backgroundColor: page === p ? '#B85C2E' : 'transparent', color: page === p ? '#fff' : '#6B7280' }}>{p}</button>
            ))}
            <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}
              className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-40">Next</button>
          </div>
        </div>
      </div>
    </div>
  )
}

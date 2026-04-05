import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Filter, Search, ChevronDown, Eye, Timer, Smile, Download } from 'lucide-react'
import { authFetch } from '../../utils/auth'
import { useReports } from '../../hooks/useReports'
import PageHeader from '../../components/PageHeader'
import StageBadge from '../../components/StageBadge'

const STAGE_OPTIONS = [
  { label: 'New',                  value: 'NEW' },
  { label: 'Pending Verification', value: 'PENDING_VERIFICATION' },
  { label: 'Verified',             value: 'VERIFIED' },
  { label: 'In Progress',          value: 'IN_PROGRESS' },
  { label: 'Awaiting Feedback',    value: 'AWAITING_FEEDBACK' },
  { label: 'Resolved',             value: 'RESOLVED' },
]

export default function ComplaintManagement() {
  const navigate = useNavigate()
  const [searchVal,   setSearchVal]   = useState('')
  const [stageFilter, setStageFilter] = useState('')
  const [dateRange,   setDateRange]   = useState('')
  const [page,        setPage]        = useState(1)
  const [exporting,   setExporting]   = useState(false)

  const LIMIT = 20
  const { reports, total, loading, error } = useReports({
    page,
    stage:     stageFilter,
    search:    searchVal,
    limit:     LIMIT,
    date_from: dateRange,
  })
  const totalPages = Math.max(1, Math.ceil(total / LIMIT))

  async function handleExport() {
    setExporting(true)
    try {
      const params = new URLSearchParams({ skip: 0, limit: 1000 })
      if (stageFilter)      params.set('stage',     stageFilter)
      if (searchVal.trim()) params.set('search',    searchVal.trim())
      if (dateRange.trim()) params.set('date_from', dateRange.trim())
      const res  = await authFetch(`/admin/reports?${params}`)
      const data = await res.json()
      const rows = data.reports || []

      const headers = ['ID', 'Title', 'Location', 'Department', 'Severity', 'Stage', 'City', 'Created At']
      const csv = [
        headers.join(','),
        ...rows.map(r => [
          r.display_id,
          `"${(r.title       || '').replace(/"/g, '""')}"`,
          `"${(r.location    || '').replace(/"/g, '""')}"`,
          r.assigned_department || '',
          r.severity || '',
          r.kanban_stage || '',
          r.assigned_city || '',
          r.created_at ? new Date(r.created_at).toLocaleDateString() : '',
        ].join(',')),
      ].join('\n')

      const blob = new Blob([csv], { type: 'text/csv' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `complaints-export-${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      // silently fail
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="p-6 flex flex-col gap-5">
      <PageHeader title="Complaint Management" subtitle="Manage and track municipal issues reported by citizens.">
        <button
          onClick={handleExport}
          disabled={exporting || loading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50 disabled:opacity-50"
        >
          <Download size={14} />
          {exporting ? 'Exporting…' : 'Export CSV'}
        </button>
      </PageHeader>

      <div className="flex gap-5">
        {/* Filters */}
        <div className="w-60 shrink-0 flex flex-col gap-4">
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <Filter size={15} className="text-gray-700" />
              <span className="font-extrabold text-gray-800">Filters</span>
            </div>
            <div>
              <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Search</p>
              <div className="flex items-center gap-2 bg-gray-100 rounded-xl px-3 py-2.5">
                <Search size={13} className="text-gray-400 shrink-0" />
                <input
                  type="text" placeholder="ID or type"
                  value={searchVal} onChange={e => { setSearchVal(e.target.value); setPage(1) }}
                  className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
                />
              </div>
            </div>
            <div>
              <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">Stage</p>
              <div className="relative">
                <select value={stageFilter} onChange={e => { setStageFilter(e.target.value); setPage(1) }}
                  className="w-full bg-gray-100 rounded-xl px-3 py-2.5 text-sm text-gray-700 outline-none appearance-none cursor-pointer">
                  <option value="">All Stages</option>
                  {STAGE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
                <ChevronDown size={13} className="absolute right-3 top-3 text-gray-400 pointer-events-none" />
              </div>
            </div>
            <div>
              <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-2">From Date</p>
              <input type="date" value={dateRange} onChange={e => { setDateRange(e.target.value); setPage(1) }}
                className="w-full bg-gray-100 rounded-xl px-3 py-2.5 text-sm text-gray-500 outline-none" />
            </div>
            <button onClick={() => { setSearchVal(''); setStageFilter(''); setDateRange(''); setPage(1) }}
              className="w-full py-2.5 rounded-xl text-sm font-semibold border border-warm-border hover:bg-gray-50 text-primary">
              Reset Filters
            </button>
          </div>
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border cursor-pointer" onClick={() => navigate('/analytics')}>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase mb-1">Total Loaded</p>
            <p className="text-4xl font-black text-gray-900 mb-3">{total}</p>
            <div className="h-1.5 rounded-full bg-gray-100">
              <div className="h-full rounded-full bg-primary" style={{ width: '60%' }} />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 flex flex-col gap-4">
          <div className="bg-white rounded-3xl shadow-sm border border-warm-border overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-50">
                  {['COMPLAINT ID', 'ISSUE TYPE', 'DEPARTMENT', 'SEVERITY', 'STATUS', 'ACTION'].map(h => (
                    <th key={h} className="text-left text-xs font-bold tracking-widest text-gray-400 px-5 py-4">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={6} className="px-5 py-10 text-center text-sm text-gray-400">Loading…</td></tr>
                ) : error ? (
                  <tr><td colSpan={6} className="px-5 py-10 text-center text-sm text-red-500">{error}</td></tr>
                ) : reports.length === 0 ? (
                  <tr><td colSpan={6} className="px-5 py-10 text-center text-sm text-gray-400">No complaints found.</td></tr>
                ) : reports.map(c => (
                  <tr key={c.id} className="border-b last:border-0 hover:bg-gray-50 cursor-pointer" onClick={() => navigate('/complaint-detail/' + c.id)}>
                    <td className="px-5 py-4 text-sm font-extrabold text-gray-800">{c.display_id}</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-xl flex items-center justify-center text-base shrink-0" style={{ backgroundColor: '#FFF7ED' }}>{c.icon}</div>
                        <div>
                          <p className="text-sm font-semibold text-gray-800">{c.title}</p>
                          <p className="text-xs text-gray-400">{c.location}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-600 capitalize">{c.assigned_department ?? '—'}</td>
                    <td className="px-5 py-4">
                      <span className="text-xs font-bold px-3 py-1 rounded-full" style={{ backgroundColor: c.severity_bg, color: c.severity_color }}>{c.severity}</span>
                    </td>
                    <td className="px-5 py-4"><StageBadge stage={c.kanban_stage} /></td>
                    <td className="px-5 py-4">
                      <button onClick={e => { e.stopPropagation(); navigate('/complaint-detail/' + c.id) }} className="text-gray-400 hover:text-gray-600">
                        <Eye size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="flex items-center justify-between px-5 py-4 border-t border-gray-50">
              <p className="text-sm text-gray-500">
                Showing <span className="font-bold text-gray-800">{Math.min((page - 1) * LIMIT + 1, total)}–{Math.min(page * LIMIT, total)}</span> of <span className="font-bold text-gray-800">{total}</span>
              </p>
              <div className="flex items-center gap-1.5">
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)} className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-40">Previous</button>
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(p => (
                  <button key={p} onClick={() => setPage(p)} className="w-8 h-8 rounded-lg text-sm font-bold"
                    style={{ backgroundColor: page === p ? '#B85C2E' : 'transparent', color: page === p ? '#fff' : '#6B7280' }}>{p}</button>
                ))}
                <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)} className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 disabled:opacity-40">Next</button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center justify-between cursor-pointer" onClick={() => navigate('/analytics')}>
              <div>
                <p className="text-sm font-bold text-gray-800">Resolution Speed</p>
                <p className="text-xs text-gray-400 mb-2">Avg time to close a ticket</p>
                <div className="flex items-end gap-2">
                  <span className="text-3xl font-black text-gray-900">42.5 hrs</span>
                  <span className="text-xs font-bold text-green-500 mb-1">↓ 4%</span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FFF7ED' }}>
                <Timer size={20} style={{ color: '#B85C2E' }} />
              </div>
            </div>
            <div className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex items-center justify-between cursor-pointer" onClick={() => navigate('/analytics')}>
              <div>
                <p className="text-sm font-bold text-gray-800">Citizen Satisfaction</p>
                <p className="text-xs text-gray-400 mb-2">Based on resolution feedback</p>
                <div className="flex items-end gap-2">
                  <span className="text-3xl font-black text-gray-900">4.8/5.0</span>
                  <span className="text-xs font-bold text-primary mb-1">Top City</span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#FFF7ED' }}>
                <Smile size={20} style={{ color: '#B85C2E' }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

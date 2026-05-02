import { useEffect, useRef, useState } from 'react'
import { authFetch } from '../../utils/auth'

export default function AnalyticsReportModal({ open, onClose, scope, scopeId, days }) {
  const [pdfUrl, setPdfUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const urlRef = useRef('')

  useEffect(() => {
    if (!open) {
      setPdfUrl('')
      setError(null)
      setLoading(false)
      return undefined
    }

    let cancelled = false
    setLoading(true)
    setError(null)
    setPdfUrl('')

    const params = new URLSearchParams({
      scope,
      scope_id: scopeId ?? '',
      days: String(days),
      disposition: 'inline',
    })

    authFetch(`/admin/analytics/report.pdf?${params}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.blob()
      })
      .then(blob => {
        if (cancelled) return
        if (urlRef.current) URL.revokeObjectURL(urlRef.current)
        urlRef.current = URL.createObjectURL(blob)
        setPdfUrl(urlRef.current)
      })
      .catch(e => {
        if (!cancelled) setError(e.message || 'Could not load report')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current)
        urlRef.current = ''
      }
    }
  }, [open, scope, scopeId, days])

  if (!open) return null

  async function handleDownload() {
    const params = new URLSearchParams({
      scope,
      scope_id: scopeId ?? '',
      days: String(days),
      disposition: 'attachment',
    })
    try {
      const res = await authFetch(`/admin/analytics/report.pdf?${params}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      const href = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = href
      a.download = 'streetlight-analytics-report.pdf'
      a.click()
      URL.revokeObjectURL(href)
    } catch {
      /* ignored */
    }
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="analytics-report-title"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl border border-warm-border w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-warm-border shrink-0">
          <div>
            <h2 id="analytics-report-title" className="text-sm font-bold text-gray-900">
              Analytics report (PDF)
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">Preview · scoped metrics, alerts, recommendations</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleDownload}
              disabled={loading || !!error || !pdfUrl}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-primary text-white hover:bg-primary-dark disabled:opacity-40 transition-colors"
            >
              Download
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-gray-200 text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>

        <div className="flex-1 min-h-[60vh] bg-gray-100 relative">
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center text-sm text-gray-500">
              Building PDF…
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center px-6 text-center text-sm text-red-600">
              {error}
            </div>
          )}
          {!loading && !error && pdfUrl && (
            <iframe title="Analytics PDF preview" src={pdfUrl} className="w-full h-full min-h-[60vh] border-0" />
          )}
        </div>
      </div>
    </div>
  )
}

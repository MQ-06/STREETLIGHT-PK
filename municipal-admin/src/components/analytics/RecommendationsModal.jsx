import { useEffect, useState } from 'react'
import { authFetchJson } from '../../utils/auth'

/** Simple priority labels — plain English anyone in Pakistan can follow. */
const PRIORITY_UI = {
  high: {
    tag: 'Do this first',
    tagUr: '(sab se pehle)',
    bar: '#DC2626',
    bg: '#FEF2F2',
  },
  medium: {
    tag: 'Do soon',
    tagUr: '(jald)',
    bar: '#D97706',
    bg: '#FFFBEB',
  },
  low: {
    tag: 'Keep in mind',
    tagUr: '(yaad rakhein)',
    bar: '#4B5563',
    bg: '#F9FAFB',
  },
}

export default function RecommendationsModal({ open, onClose, scope, scopeId, days }) {
  const [payload, setPayload] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!open) {
      setPayload(null)
      setError(null)
      return undefined
    }

    let cancelled = false
    setLoading(true)
    setError(null)
    const params = new URLSearchParams({
      scope,
      scope_id: scopeId ?? '',
      days: String(days),
    })
    authFetchJson(`/admin/analytics/recommendations?${params}`)
      .then(d => {
        if (!cancelled) {
          setPayload(d)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Could not load recommendations. Check your connection and try again.')
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [open, scope, scopeId, days])

  if (!open) return null

  const recs = payload?.recommendations ?? []

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="rec-modal-title"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl border border-warm-border w-full max-w-lg max-h-[85vh] flex flex-col overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        <div className="px-5 py-4 border-b border-warm-border shrink-0 bg-gradient-to-r from-orange-50 to-white">
          <h2 id="rec-modal-title" className="text-lg font-black text-gray-900">
            Next steps from your data
          </h2>
          <p className="text-xs text-gray-600 mt-1 leading-relaxed">
            Tips come straight from complaint counts you already saved — short sentences, real numbers inside each card.
          </p>
          {payload?.scope_label && (
            <p className="text-[11px] text-gray-500 mt-2">
              Area: {payload.scope_label} · Last {days} days
            </p>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {loading && (
            <div className="space-y-3">
              {[0, 1, 2].map(i => (
                <div key={i} className="h-20 rounded-xl bg-gray-100 animate-pulse" />
              ))}
            </div>
          )}
          {error && <p className="text-sm text-red-600 text-center py-6">{error}</p>}
          {!loading && !error && recs.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-6">No tips for this period.</p>
          )}
          {!loading &&
            !error &&
            recs.map((r, i) => {
              const st = PRIORITY_UI[r.priority] ?? PRIORITY_UI.low
              return (
                <div
                  key={i}
                  className="rounded-xl border border-gray-100 overflow-hidden"
                  style={{ backgroundColor: st.bg }}
                >
                  <div className="flex items-center gap-2 px-4 py-2 border-b border-black/5">
                    <span className="w-1 self-stretch rounded-full shrink-0" style={{ background: st.bar }} />
                    <div>
                      <span
                        className="text-[10px] font-bold uppercase tracking-wide"
                        style={{ color: st.bar }}
                      >
                        {st.tag}
                      </span>
                      <span className="text-[10px] text-gray-500 ml-1">{st.tagUr}</span>
                    </div>
                  </div>
                  <div className="px-4 py-3">
                    <p className="text-base font-bold text-gray-900 leading-snug">{r.title}</p>
                    <p className="text-sm text-gray-800 mt-2 leading-relaxed">{r.detail}</p>
                  </div>
                </div>
              )
            })}
        </div>

        <div className="px-5 py-3 border-t border-warm-border shrink-0 bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2.5 rounded-xl text-sm font-bold bg-primary text-white hover:bg-primary-dark transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

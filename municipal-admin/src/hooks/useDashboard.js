import { useState, useEffect } from 'react'
import { authFetchJson } from '../utils/auth'

export function useDashboard() {
  const [data,    setData]    = useState(null)
  const [trend,   setTrend]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [overview, analytics] = await Promise.all([
          authFetchJson('/admin/dashboard/overview'),
          authFetchJson('/admin/dashboard/analytics?days=7'),
        ])
        if (!cancelled) {
          setData(overview)
          setTrend(analytics.trend || [])
        }
      } catch {
        if (!cancelled) setError('Failed to load overview.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => { cancelled = true }
  }, [])

  return { data, trend, loading, error }
}

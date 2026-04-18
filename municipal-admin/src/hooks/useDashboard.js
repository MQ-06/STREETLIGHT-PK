import { useState, useEffect } from 'react'
import { authFetch } from '../utils/auth'

export function useDashboard() {
  const [data,    setData]    = useState(null)
  const [trend,   setTrend]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    Promise.all([
      authFetch('/admin/dashboard/overview').then(r => r.json()),
      authFetch('/admin/dashboard/analytics?days=7').then(r => r.json()),
    ])
      .then(([overview, analytics]) => {
        setData(overview)
        setTrend(analytics.trend || [])
        setLoading(false)
      })
      .catch(() => { setError('Failed to load overview.'); setLoading(false) })
  }, [])

  return { data, trend, loading, error }
}

import { useState, useEffect } from 'react'
import { authFetch } from '../utils/auth'

export function useDashboard() {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    authFetch('/admin/dashboard/overview')
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false) })
      .catch(() => { setError('Failed to load overview.'); setLoading(false) })
  }, [])

  return { data, loading, error }
}

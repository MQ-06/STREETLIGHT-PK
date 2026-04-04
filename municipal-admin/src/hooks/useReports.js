import { useState, useEffect, useCallback } from 'react'
import { authFetch } from '../utils/auth'

export function useReports({ page = 1, stage = '', search = '', limit = 20 } = {}) {
  const [reports, setReports] = useState([])
  const [total,   setTotal]   = useState(0)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const skip   = (page - 1) * limit
      const params = new URLSearchParams({ skip, limit })
      if (stage)        params.set('stage',  stage)
      if (search.trim()) params.set('search', search.trim())
      const res  = await authFetch(`/admin/reports?${params}`)
      const data = await res.json()
      setReports(data.reports || [])
      setTotal(data.total   || 0)
    } catch {
      setError('Failed to load reports.')
    } finally {
      setLoading(false)
    }
  }, [page, stage, search, limit])

  useEffect(() => { load() }, [load])

  return { reports, total, loading, error, refetch: load }
}

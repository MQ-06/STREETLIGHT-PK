/**
 * useMapReports — M0: Data layer for the Hotspot Map
 *
 * Fetches up to 500 reports with GPS from /admin/reports (scoped by admin role).
 * Re-fetches when stage filter or global admin search query changes.
 * Category, severity, timeRange stay client-side.
 */
import { useState, useEffect, useCallback } from 'react'
import { authFetch } from '../utils/auth'
import { useAdminSearch } from '../context/AdminSearchContext'

const DEFAULT_FILTERS = {
  category:  '',
  stage:     '',
  severity:  '',
  timeRange: '30d',
}

function cutoffFor(timeRange) {
  const now = Date.now()
  if (timeRange === '24h') return now - 24 * 60 * 60 * 1000
  if (timeRange === '7d')  return now - 7  * 24 * 60 * 60 * 1000
  return now - 30 * 24 * 60 * 60 * 1000
}

function applyFilters(reports, filters) {
  const cutoff = cutoffFor(filters.timeRange)

  return reports.filter(r => {
    if (r.created_at) {
      const ts = new Date(r.created_at).getTime()
      if (ts < cutoff) return false
    }
    if (filters.category && r.category !== filters.category) return false
    if (filters.severity && r.ai_severity !== filters.severity) return false
    return true
  })
}

export default function useMapReports() {
  const { query: searchQuery } = useAdminSearch()
  const [allReports, setAllReports] = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [filters,    setFilters]    = useState(DEFAULT_FILTERS)

  const fetchReports = useCallback(async (stage, search) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: 500 })
      if (stage) params.set('stage', stage)
      if (search && search.trim()) params.set('search', search.trim())

      const res  = await authFetch(`/admin/reports?${params}`)

      if (!res.ok) {
        console.warn('[useMapReports] fetch failed:', res.status)
        return
      }

      const data = await res.json()

      const withGps = (data.reports || []).filter(
        r => r.lat != null && r.lng != null
      )
      setAllReports(withGps)
    } catch (err) {
      setError('Failed to load map reports.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchReports(filters.stage, searchQuery)
  }, [filters.stage, searchQuery, fetchReports])

  const setFilter = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }, [])

  const refetch = useCallback(() => {
    fetchReports(filters.stage, searchQuery)
  }, [filters.stage, searchQuery, fetchReports])

  const filtered = applyFilters(allReports, filters)

  return { allReports, filtered, loading, error, filters, setFilter, refetch }
}

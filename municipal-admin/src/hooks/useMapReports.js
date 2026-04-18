/**
 * useMapReports — M0: Data layer for the Hotspot Map
 *
 * Single source of truth for every map UI module.
 * - Fetches up to 500 reports with GPS coords from /admin/reports
 * - Re-fetches from server only when `stage` filter changes
 * - All other filters (category, severity, timeRange) are applied client-side
 *
 * Returns:
 *   allReports  — raw GPS-valid reports from last fetch
 *   filtered    — allReports after all client-side filters applied
 *   loading     — true while fetching
 *   error       — error message string or null
 *   filters     — current filter state object
 *   setFilter   — (key, value) => void  update one filter key
 *   refetch     — () => void  force a fresh server fetch
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { authFetch } from '../utils/auth'

// ── Default filter state ──────────────────────────────────────────────────────
const DEFAULT_FILTERS = {
  category:  '',      // '' | 'POTHOLE' | 'TRASH'
  stage:     '',      // '' | 'NEW' | 'PENDING_VERIFICATION' | 'VERIFIED' |
                      //     'IN_PROGRESS' | 'AWAITING_FEEDBACK' | 'RESOLVED'
  severity:  '',      // '' | 'small' | 'medium' | 'large'
  timeRange: '30d',   // '24h' | '7d' | '30d'
}

// ── Time-range helper ─────────────────────────────────────────────────────────
function cutoffFor(timeRange) {
  const now = Date.now()
  if (timeRange === '24h') return now - 24 * 60 * 60 * 1000
  if (timeRange === '7d')  return now - 7  * 24 * 60 * 60 * 1000
  return now - 30 * 24 * 60 * 60 * 1000   // default 30d
}

// ── Client-side filter application ───────────────────────────────────────────
function applyFilters(reports, filters) {
  const cutoff = cutoffFor(filters.timeRange)

  return reports.filter(r => {
    // timeRange
    if (r.created_at) {
      const ts = new Date(r.created_at).getTime()
      if (ts < cutoff) return false
    }

    // category
    if (filters.category && r.category !== filters.category) return false

    // severity  (stored as ai_severity on the report)
    if (filters.severity && r.ai_severity !== filters.severity) return false

    return true
  })
}

// ── Hook ──────────────────────────────────────────────────────────────────────
export default function useMapReports() {
  const [allReports, setAllReports] = useState([])
  const [loading,    setLoading]    = useState(true)
  const [error,      setError]      = useState(null)
  const [filters,    setFilters]    = useState(DEFAULT_FILTERS)

  // Track previous stage to know when to re-fetch
  const prevStageRef = useRef(filters.stage)

  // ── Fetch from server ───────────────────────────────────────────────────────
  const fetchReports = useCallback(async (stage) => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: 500 })
      if (stage) params.set('stage', stage)

      const res  = await authFetch(`/admin/reports?${params}`)
      const data = await res.json()

      // Keep only reports that have valid GPS coordinates
      // API serialises coordinates as `lat` / `lng`
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

  // Initial fetch
  useEffect(() => {
    fetchReports(filters.stage)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Re-fetch only when stage changes (server-side filter)
  useEffect(() => {
    if (filters.stage !== prevStageRef.current) {
      prevStageRef.current = filters.stage
      fetchReports(filters.stage)
    }
  }, [filters.stage, fetchReports])

  // ── setFilter: update a single filter key ────────────────────────────────
  const setFilter = useCallback((key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }, [])

  // ── refetch: force fresh server call with current stage ───────────────────
  const refetch = useCallback(() => {
    fetchReports(filters.stage)
  }, [filters.stage, fetchReports])

  // ── Apply client-side filters ─────────────────────────────────────────────
  const filtered = applyFilters(allReports, filters)

  return { allReports, filtered, loading, error, filters, setFilter, refetch }
}

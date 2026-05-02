import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { useLocation } from 'react-router-dom'

const AdminSearchContext = createContext(null)

const DEBOUNCE_MS = 350

export function AdminSearchProvider({ children }) {
  const location = useLocation()
  const [draft, setDraft] = useState('')
  const [query, setQuery] = useState('')

  useEffect(() => {
    const t = setTimeout(() => setQuery(draft.trim()), DEBOUNCE_MS)
    return () => clearTimeout(t)
  }, [draft])

  const clearSearch = useCallback(() => {
    setDraft('')
  }, [])

  useEffect(() => {
    if (!location.pathname.includes('complaint-management')) return
    const params = new URLSearchParams(location.search)
    const q = params.get('search')
    if (q !== null) setDraft(q)
  }, [location.pathname, location.search])

  const value = useMemo(
    () => ({
      draft,
      setDraft,
      query,
      clearSearch,
    }),
    [draft, query, clearSearch]
  )

  return (
    <AdminSearchContext.Provider value={value}>
      {children}
    </AdminSearchContext.Provider>
  )
}

export function useAdminSearch() {
  const ctx = useContext(AdminSearchContext)
  if (!ctx) {
    throw new Error('useAdminSearch must be used inside AdminSearchProvider')
  }
  return ctx
}

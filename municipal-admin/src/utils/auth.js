const TOKEN_KEY = 'admin_access_token'
const USER_KEY  = 'admin_user'

export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
}

export function setAuthData(accessToken, user) {
  localStorage.setItem(TOKEN_KEY, accessToken)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearAuthData() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getCurrentUser() {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try { return JSON.parse(raw) } catch { return null }
}

export function isAuthenticated() {
  return Boolean(getToken())
}

// ── Role helpers ────────────────────────────────────────────────────────────

export function getRole() {
  return getCurrentUser()?.role ?? null
}

export function getCity() {
  return getCurrentUser()?.city ?? null
}

export function getDepartment() {
  return getCurrentUser()?.department ?? null
}

export function isSuperAdmin() {
  return getRole() === 'super_admin'
}

export function isCityAdmin() {
  return getRole() === 'city_admin'
}

export function isDeptOfficer() {
  return getRole() === 'dept_officer'
}

export function hasRole(...roles) {
  return roles.includes(getRole())
}

// ── Authenticated fetch ──────────────────────────────────────────────────────
// Wrapper that injects the Bearer token on every request.

export async function authFetch(path, options = {}) {
  const token = getToken()
  const base  = getApiBaseUrl()
  const url   = path.startsWith('http') ? path : `${base}${path}`

  const isFormData =
    typeof FormData !== 'undefined' && options.body instanceof FormData

  const res = await fetch(url, {
    ...options,
    headers: {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  if (res.status === 401) {
    clearAuthData()
    window.location.href = '/signin'
  }

  return res
}

/** JSON body only when response is OK; otherwise rejects (401 still clears session via authFetch). */
export async function authFetchJson(path, options = {}) {
  const res = await authFetch(path, options)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

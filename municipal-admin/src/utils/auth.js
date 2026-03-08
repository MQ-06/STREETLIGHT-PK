const TOKEN_KEY = 'admin_access_token'
const USER_KEY = 'admin_user'

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
  const rawUser = localStorage.getItem(USER_KEY)
  if (!rawUser) return null

  try {
    return JSON.parse(rawUser)
  } catch {
    return null
  }
}

export function isAuthenticated() {
  return Boolean(getToken())
}

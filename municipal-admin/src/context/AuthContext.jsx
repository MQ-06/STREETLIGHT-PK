import { createContext, useContext, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getCurrentUser, getToken, clearAuthData, setAuthData,
  getRole, getCity, getDepartment, hasRole,
} from '../utils/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getCurrentUser())
  const navigate = useNavigate()

  const login = useCallback((token, userData) => {
    setAuthData(token, userData)
    setUser(userData)
  }, [])

  const logout = useCallback(() => {
    clearAuthData()
    setUser(null)
    navigate('/signin', { replace: true })
  }, [navigate])

  // Convenience derived values
  const role       = user?.role       ?? null
  const city       = user?.city       ?? null
  const department = user?.department ?? null

  const value = {
    user,
    role,
    city,
    department,
    isAuthenticated: Boolean(getToken()),
    isSuperAdmin:    role === 'super_admin',
    isCityAdmin:     role === 'city_admin',
    isDeptOfficer:   role === 'dept_officer',
    canSeeAllCities: role === 'super_admin',
    hasRole:         (...roles) => roles.includes(role),
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}

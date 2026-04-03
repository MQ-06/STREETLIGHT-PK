import { createBrowserRouter, Navigate } from 'react-router-dom'
import Layout from '../layouts/Layout'
import SignIn from '../pages/SignIn'
import Dashboard from '../pages/Dashboard'
import HotspotMap from '../pages/HotspotMap'
import ComplaintDetail from '../pages/ComplaintDetail'
import ComplaintManagement from '../pages/ComplaintManagement'
import ResolutionBoard from '../pages/ResolutionBoard'
import Analytics from '../pages/Analytics'
import Transparency from '../pages/Transparency'
import Departments from '../pages/Departments'
import UserRoles from '../pages/UserRoles'
import { AuthProvider } from '../context/AuthContext'
import { isAuthenticated, hasRole } from '../utils/auth'

// ── Guards ───────────────────────────────────────────────────────────────────

function ProtectedRoute({ children, roles }) {
  if (!isAuthenticated()) return <Navigate to="/signin" replace />
  if (roles && !hasRole(...roles)) return <Navigate to="/dashboard" replace />
  return children
}

function PublicOnlyRoute({ children }) {
  if (isAuthenticated()) return <Navigate to="/dashboard" replace />
  return children
}

// ── AuthProvider wrapper (needs to be inside RouterProvider for useNavigate) ─

function WithAuth({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

// ── Router ───────────────────────────────────────────────────────────────────

const router = createBrowserRouter([
  // Public
  {
    path: '/signin',
    element: (
      <WithAuth>
        <PublicOnlyRoute><SignIn /></PublicOnlyRoute>
      </WithAuth>
    ),
  },

  // Authenticated — inside layout
  {
    path: '/',
    element: (
      <WithAuth>
        <ProtectedRoute><Layout /></ProtectedRoute>
      </WithAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },

      // All admin roles
      { path: 'dashboard',            element: <Dashboard /> },
      { path: 'complaint-management', element: <ComplaintManagement /> },
      { path: 'complaint-detail/:id', element: <ComplaintDetail /> },
      { path: 'complaint-detail',     element: <ComplaintDetail /> },
      { path: 'resolution-board',     element: <ResolutionBoard /> },
      { path: 'hotspot-map',          element: <HotspotMap /> },
      { path: 'analytics',            element: <Analytics /> },
      { path: 'transparency',         element: <Transparency /> },

      // super_admin + city_admin only
      {
        path: 'departments',
        element: (
          <ProtectedRoute roles={['super_admin', 'city_admin']}>
            <Departments />
          </ProtectedRoute>
        ),
      },

      // super_admin only
      {
        path: 'user-roles',
        element: (
          <ProtectedRoute roles={['super_admin']}>
            <UserRoles />
          </ProtectedRoute>
        ),
      },

      { path: '*', element: <Navigate to="/dashboard" replace /> },
    ],
  },

  { path: '*', element: <Navigate to="/signin" replace /> },
])

export default router

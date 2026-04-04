import { createBrowserRouter, Navigate } from 'react-router-dom'
import Layout      from '../layouts/Layout'
import SignIn      from '../pages/SignIn'
import Dashboard   from '../pages/Dashboard'
import Departments from '../pages/Departments'
import UserRoles   from '../pages/UserRoles'
import ComplaintManagement from '../pages/shared/ComplaintManagement'
import ComplaintDetail     from '../pages/shared/ComplaintDetail'
import ResolutionBoard     from '../pages/shared/ResolutionBoard'
import HotspotMap          from '../pages/shared/HotspotMap'
import Analytics           from '../pages/shared/Analytics'
import Transparency        from '../pages/shared/Transparency'
import { AuthProvider }    from '../context/AuthContext'
import { isAuthenticated, hasRole } from '../utils/auth'

function ProtectedRoute({ children, roles }) {
  if (!isAuthenticated()) return <Navigate to="/signin" replace />
  if (roles && !hasRole(...roles)) return <Navigate to="/dashboard" replace />
  return children
}

function PublicOnlyRoute({ children }) {
  if (isAuthenticated()) return <Navigate to="/dashboard" replace />
  return children
}

function WithAuth({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

const router = createBrowserRouter([
  {
    path: '/signin',
    element: <WithAuth><PublicOnlyRoute><SignIn /></PublicOnlyRoute></WithAuth>,
  },
  {
    path: '/',
    element: <WithAuth><ProtectedRoute><Layout /></ProtectedRoute></WithAuth>,
    children: [
      { index: true,                       element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard',                 element: <Dashboard /> },
      { path: 'complaint-management',      element: <ComplaintManagement /> },
      { path: 'complaint-detail/:id',      element: <ComplaintDetail /> },
      { path: 'complaint-detail',          element: <ComplaintDetail /> },
      { path: 'resolution-board',          element: <ResolutionBoard /> },
      { path: 'hotspot-map',               element: <HotspotMap /> },
      { path: 'analytics',                 element: <Analytics /> },
      { path: 'transparency',              element: <Transparency /> },
      {
        path: 'departments',
        element: <ProtectedRoute roles={['super_admin', 'city_admin']}><Departments /></ProtectedRoute>,
      },
      {
        path: 'user-roles',
        element: <ProtectedRoute roles={['super_admin']}><UserRoles /></ProtectedRoute>,
      },
      { path: '*', element: <Navigate to="/dashboard" replace /> },
    ],
  },
  { path: '*', element: <Navigate to="/signin" replace /> },
])

export default router

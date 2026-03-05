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

const router = createBrowserRouter([
  // ── Public — no layout
  { path: '/signin', element: <SignIn /> },

  // ── Authenticated — inside layout
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true,                  element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard',            element: <Dashboard /> },
      { path: 'hotspot-map',          element: <HotspotMap /> },
      { path: 'complaint-detail',     element: <ComplaintDetail /> },
      { path: 'complaint-management', element: <ComplaintManagement /> },
      { path: 'resolution-board',     element: <ResolutionBoard /> },
      { path: 'analytics',            element: <Analytics /> },
      { path: 'transparency',         element: <Transparency /> },
      { path: 'departments',          element: <Departments /> },
      { path: 'user-roles',           element: <UserRoles /> },
      { path: '*',                    element: <Navigate to="/dashboard" replace /> },
    ],
  },

  // ── Catch all — redirect to signin
  { path: '*', element: <Navigate to="/signin" replace /> },
])

export default router
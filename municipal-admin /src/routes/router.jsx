import { createBrowserRouter, Navigate } from 'react-router-dom'
import SignIn from '../pages/SignIn'
import HotspotMap from '../pages/HotspotMap'
import ComplaintDetail from '../pages/ComplaintDetail'
import ResolutionBoard from '../pages/ResolutionBoard'
import Dashboard from '../pages/Dashboard'

const router = createBrowserRouter([
  { path: '/signin',            element: <SignIn /> },
  { path: '/dashboard',         element: <Dashboard /> },
  { path: '/hotspot-map',       element: <HotspotMap /> },
  { path: '/complaint-detail',  element: <ComplaintDetail /> },
  { path: '/resolution-board',  element: <ResolutionBoard /> },
  { path: '/',                  element: <Navigate to="/signin" replace /> },
])

export default router

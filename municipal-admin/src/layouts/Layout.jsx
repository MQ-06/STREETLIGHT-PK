import { Outlet } from 'react-router-dom'

function Layout() {
  return (
    <div className="h-screen w-screen overflow-hidden">
      <Outlet />
    </div>
  )
}

export default Layout
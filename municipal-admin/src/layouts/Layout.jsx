import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Topbar  from '../components/Topbar'
import GlobalLoader from '../components/GlobalLoader'

export default function Layout() {
  return (
    <>
      <GlobalLoader />
      <div className="flex h-screen overflow-hidden" style={{ backgroundColor: '#F7F6E8' }}>
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0">
          <Topbar />
          <main className="flex-1 overflow-y-auto relative animate-[fadeIn_0.3s_ease-out]">
            <Outlet />
          </main>
        </div>
      </div>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  )
}

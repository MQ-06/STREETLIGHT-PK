import { useRouteError, useNavigate } from 'react-router-dom'
import { AlertOctagon, RotateCcw, Home } from 'lucide-react'

export default function ErrorBoundary() {
  const error = useRouteError()
  const navigate = useNavigate()

  // Format the error message based on throwing type
  const errorMessage = error?.statusText || error?.message || 'An unexpected error occurred.'

  return (
    <div className="min-h-screen flex items-center justify-center p-6" style={{ backgroundColor: '#F7F6E8' }}>
      <div className="max-w-md w-full bg-white rounded-3xl p-8 shadow-sm border border-warm-border text-center flex flex-col items-center">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-sm" style={{ backgroundColor: '#FEF2F2', color: '#EF4444' }}>
          <AlertOctagon size={32} />
        </div>
        
        <h1 className="text-2xl font-black text-gray-900 mb-2">Oops! Something went wrong.</h1>
        <p className="text-sm text-gray-500 mb-6">
          The application encountered an unexpected error. Please try refreshing or return to the dashboard.
        </p>

        <div className="bg-gray-50 rounded-xl p-4 w-full mb-6 border border-warm-border text-left overflow-x-auto">
          <p className="text-xs font-mono text-red-500 font-medium whitespace-pre-wrap">{errorMessage}</p>
        </div>

        <div className="flex gap-3 w-full">
          <button 
            onClick={() => window.location.reload()}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl border border-warm-border text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <RotateCcw size={15} />
            Refresh
          </button>
          <button 
            onClick={() => navigate('/dashboard', { replace: true })}
            className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-white text-sm font-semibold transition-colors"
            style={{ backgroundColor: '#B85C2E' }}
          >
            <Home size={15} />
            Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}

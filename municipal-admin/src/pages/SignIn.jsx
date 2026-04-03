import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff } from 'lucide-react'
import { getApiBaseUrl, setAuthData, clearAuthData } from '../utils/auth'

function SignIn() {
  const [showPassword, setShowPassword] = useState(false)
  const [email,        setEmail]        = useState('')
  const [password,     setPassword]     = useState('')
  const [isLoading,    setIsLoading]    = useState(false)
  const [error,        setError]        = useState('')
  const navigate = useNavigate()

  async function handleSignIn(event) {
    event.preventDefault()
    setError('')

    if (!email.trim() || !password.trim()) {
      setError('Please enter your email and password.')
      return
    }

    setIsLoading(true)
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/auth/login`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email: email.trim(), password }),
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Sign in failed.')

      clearAuthData()
      // data.user now includes role, city, department from backend
      setAuthData(data.access_token, data.user)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message || 'Sign in failed.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#f7f6e8' }}>

      {/* TOP NAV */}
      <header className="flex items-center justify-between px-8 py-3 shrink-0">
        <div className="flex items-center gap-2">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: '#ede8dc' }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#b85c2a" />
              <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#b85c2a" />
              <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#b85c2a" />
              <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#b85c2a" />
            </svg>
          </div>
          <span
            className="font-extrabold text-sm tracking-widest uppercase"
            style={{ color: '#b85c2a' }}
          >
            Streetlight
          </span>
        </div>
      </header>

      {/* MAIN */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">

        <div
          className="w-16 h-16 rounded-full flex items-center justify-center mb-3"
          style={{ backgroundColor: '#ede8dc' }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <rect x="2"  y="10" width="3" height="11" rx="0.5" fill="#b85c2a" />
            <rect x="7"  y="6"  width="3" height="15" rx="0.5" fill="#b85c2a" />
            <rect x="12" y="8"  width="3" height="13" rx="0.5" fill="#b85c2a" />
            <rect x="17" y="4"  width="3" height="17" rx="0.5" fill="#b85c2a" />
          </svg>
        </div>

        <h1 className="text-3xl font-extrabold text-gray-900 mb-1 tracking-tight">
          Welcome Back
        </h1>
        <p className="text-sm text-gray-500 text-center mb-5 leading-relaxed">
          Manage city reports and accountability from your dashboard.
        </p>

        <form
          onSubmit={handleSignIn}
          className="bg-white rounded-3xl shadow-md px-8 py-6 w-full max-w-md flex flex-col gap-4"
        >
          {/* Email */}
          <div className="flex flex-col gap-1">
            <label className="text-sm font-semibold text-gray-800">Email Address</label>
            <div className="flex items-center gap-3 bg-gray-100 rounded-full px-4 py-2.5">
              <Mail size={15} className="text-gray-400 shrink-0" />
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="officer@streetlight.local"
                className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
                autoComplete="email"
              />
            </div>
          </div>

          {/* Password */}
          <div className="flex flex-col gap-1">
            <label className="text-sm font-semibold text-gray-800">Password</label>
            <div className="flex items-center gap-3 bg-gray-100 rounded-full px-4 py-2.5">
              <Lock size={15} className="text-gray-400 shrink-0" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(p => !p)}
                className="text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 rounded-full text-white font-semibold text-sm tracking-wide transition hover:opacity-90 active:scale-95"
            style={{ backgroundColor: '#b85c2a' }}
          >
            {isLoading ? 'Signing In…' : 'Sign In'}
          </button>

          {error && (
            <p className="text-sm text-red-600 text-center">{error}</p>
          )}
        </form>
      </main>

      {/* FOOTER */}
      <footer className="py-3 text-center shrink-0" style={{ backgroundColor: '#dddbd0' }}>
        <p className="text-xs tracking-widest uppercase mb-1.5" style={{ color: '#a0a0a0' }}>
          Streetlight Civic Dash V2.0
        </p>
        <div className="flex items-center justify-center gap-8 text-xs" style={{ color: '#a0a0a0' }}>
          <a href="#" className="hover:text-gray-600">Privacy Policy</a>
          <a href="#" className="hover:text-gray-600">Terms of Service</a>
          <a href="#" className="hover:text-gray-600">Help Center</a>
        </div>
      </footer>

    </div>
  )
}

export default SignIn

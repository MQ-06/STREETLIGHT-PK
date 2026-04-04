import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, ShieldCheck, BarChart2, Map } from 'lucide-react'
import { getApiBaseUrl, setAuthData, clearAuthData } from '../utils/auth'

const FEATURES = [
  { icon: ShieldCheck, text: 'AI-powered complaint validation' },
  { icon: BarChart2,   text: 'Real-time analytics dashboard'  },
  { icon: Map,         text: 'Live hotspot map & routing'     },
]

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
      setAuthData(data.access_token, data.user)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.message || 'Sign in failed.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="h-screen flex overflow-hidden" style={{ backgroundColor: '#F7F6E8' }}>

      {/* ── Left panel ───────────────────────────────────────────────────── */}
      <div
        className="hidden lg:flex flex-col justify-between w-[480px] shrink-0 p-12"
        style={{ backgroundColor: '#B85C2E' }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3">
          <img src="/logo.jpg" alt="StreetLight" className="w-10 h-10 rounded-xl object-cover" />
          <div>
            <p className="font-black text-white text-lg leading-tight tracking-tight">StreetLight</p>
            <p className="text-xs font-medium" style={{ color: 'rgba(255,255,255,0.6)' }}>Admin Portal</p>
          </div>
        </div>

        {/* Hero content */}
        <div>
          <h1 className="text-4xl font-black text-white leading-tight mb-4">
            Smarter Cities<br />Start Here.
          </h1>
          <p className="text-base leading-relaxed mb-10" style={{ color: 'rgba(255,255,255,0.75)' }}>
            Manage civic complaints, track municipal performance,
            and drive accountability across Pakistan's cities.
          </p>
          <div className="flex flex-col gap-4">
            {FEATURES.map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                     style={{ backgroundColor: 'rgba(255,255,255,0.15)' }}>
                  <Icon size={15} className="text-white" />
                </div>
                <span className="text-sm font-medium" style={{ color: 'rgba(255,255,255,0.85)' }}>{text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <p className="text-xs" style={{ color: 'rgba(255,255,255,0.4)' }}>
          © 2025 StreetLight — FYP Capstone Project
        </p>
      </div>

      {/* ── Right panel ──────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 overflow-y-auto">

        {/* Mobile logo */}
        <div className="lg:hidden flex items-center gap-2.5 mb-8">
          <img src="/logo.jpg" alt="StreetLight" className="w-10 h-10 rounded-xl object-cover" />
          <span className="font-black text-xl text-primary tracking-tight">StreetLight</span>
        </div>

        {/* Logo mark (desktop) */}
        <div className="hidden lg:flex mb-6 items-center justify-center w-20 h-20 rounded-3xl shadow-lg overflow-hidden"
             style={{ backgroundColor: '#fff' }}>
          <img src="/logo.jpg" alt="StreetLight" className="w-full h-full object-cover" />
        </div>

        <h2 className="text-3xl font-black text-gray-900 mb-1 tracking-tight">Welcome back</h2>
        <p className="text-sm text-gray-500 mb-8">Sign in to your municipal admin account</p>

        <form onSubmit={handleSignIn}
              className="bg-white rounded-3xl shadow-sm border border-warm-border px-8 py-8 w-full max-w-sm flex flex-col gap-5">

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-semibold text-gray-700">Email</label>
            <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 py-3 border border-warm-border focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/10 transition-all">
              <Mail size={15} className="text-gray-400 shrink-0" />
              <input
                type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="officer@streetlight.local"
                className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
                autoComplete="email"
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-semibold text-gray-700">Password</label>
            <div className="flex items-center gap-3 bg-gray-50 rounded-2xl px-4 py-3 border border-warm-border focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/10 transition-all">
              <Lock size={15} className="text-gray-400 shrink-0" />
              <input
                type={showPassword ? 'text' : 'password'} value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
                autoComplete="current-password"
              />
              <button type="button" onClick={() => setShowPassword(p => !p)}
                      className="text-gray-400 hover:text-gray-600 transition-colors">
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-100 rounded-2xl px-4 py-3">
              <span className="text-xs font-medium text-red-600">{error}</span>
            </div>
          )}

          <button
            type="submit" disabled={isLoading}
            className="w-full py-3.5 rounded-2xl text-white font-bold text-sm tracking-wide transition-all hover:opacity-90 active:scale-[0.98] disabled:opacity-60 shadow-sm"
            style={{ backgroundColor: '#B85C2E', boxShadow: '0 4px 14px rgba(184,92,46,0.3)' }}
          >
            {isLoading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p className="mt-6 text-xs text-gray-400">
          StreetLight Civic Platform · Municipal Admin v2.0
        </p>
      </div>
    </div>
  )
}

export default SignIn

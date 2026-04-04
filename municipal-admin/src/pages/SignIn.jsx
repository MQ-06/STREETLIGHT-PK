import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, ShieldCheck, Map, Zap, MapPin, Activity, CheckCircle2 } from 'lucide-react'
import { getApiBaseUrl, setAuthData, clearAuthData } from '../utils/auth'

const FEATURES = [
  { icon: Zap,         text: 'Instant automated fault detection' },
  { icon: Map,         text: 'Live geofenced hotspot tracking'    },
  { icon: ShieldCheck, text: 'AI-validated civic reporting'      },
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
    <div className="min-h-screen w-full flex bg-[#F7F6E8]">
      <style>{`
        @keyframes float-slow {
          0%, 100% { transform: translateY(0) rotate(-2deg); }
          50% { transform: translateY(-15px) rotate(-1deg); }
        }
        @keyframes float-slower {
          0%, 100% { transform: translateY(0) rotate(3deg) translateX(20px); }
          50% { transform: translateY(-10px) rotate(4deg) translateX(20px); }
        }
      `}</style>
      
      {/* ── Left panel (Minimal Streetlight + UI Showcase Theme) ── */}
      <div className="hidden lg:flex flex-col relative w-1/2 shrink-0 overflow-hidden bg-[#181412] text-white shadow-2xl z-10">
        
        {/* Soft atmospheric light glow */}
        <div className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-gradient-to-br from-[#B85C2E]/25 to-transparent rounded-full blur-[120px] pointer-events-none z-0"></div>

        {/* Header / Logo */}
        <div className="p-12 relative z-20 flex items-center gap-3">
          <img src="/logo.jpg" alt="StreetLight" className="w-10 h-10 rounded-xl object-cover ring-1 ring-white/20" />
          <span className="font-black text-xl tracking-tight text-white">StreetLight</span>
        </div>

        {/* Content Wrapper */}
        <div className="flex-1 flex px-16 relative z-20 items-center justify-between">
          
          {/* Left Text Column */}
          <div className="flex flex-col w-full max-w-sm">
            {/* Minimalist Streetlight SVG */}
            <div className="mb-8 relative pl-2">
              <svg width="40" height="52" viewBox="0 0 48 64" fill="none" xmlns="http://www.w3.org/2000/svg" className="drop-shadow-2xl">
                <path d="M12 64V24C12 10.7452 22.7452 0 36 0H48V4H36C24.9543 4 16 12.9543 16 24V64H12Z" fill="white" fillOpacity="0.9"/>
                <path d="M32 4H48V12H32V4Z" fill="white"/>
                <path d="M34 12H46V16C46 19.3137 43.3137 22 40 22C36.6863 22 34 19.3137 34 16V12Z" fill="#FDE68A"/>
              </svg>
              {/* Direct bulb glow */}
              <div className="absolute top-[8px] left-[26px] w-[30px] h-[30px] bg-amber-400/40 blur-[12px] rounded-full pointer-events-none"></div>
            </div>

            <h1 className="text-5xl font-black text-white leading-[1.1] mb-6 tracking-tight drop-shadow-sm">
              Illuminating<br/>city operations.
            </h1>
            
            <p className="text-base text-white/60 font-medium leading-relaxed mb-10 w-4/5 pt-2">
              A unified platform to manage civic complaints, resolve infrastructure issues, and bring complete transparency to municipal workflows.
            </p>

            <div className="flex flex-col gap-5">
              {FEATURES.map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-center gap-4">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 bg-white/5 border border-white/10 group-hover:bg-[#B85C2E]/20 transition-colors">
                    <Icon size={16} className="text-[#FDE68A]" />
                  </div>
                  <span className="text-sm font-semibold text-white/80">{text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Floating App App UI Showcase */}
          <div className="absolute right-[-15%] top-1/2 transform -translate-y-1/2 w-[420px] pointer-events-none z-10 flex flex-col gap-6">
            
            {/* UI Mock: Complaint Card 1 */}
            <div className="bg-[#FDFDFD] rounded-3xl p-6 shadow-[0_20px_40px_rgba(0,0,0,0.5)] border border-white/10"
                 style={{ animation: 'float-slow 8s ease-in-out infinite' }}>
              <div className="flex justify-between items-center mb-3">
                <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Report #SL-4092</span>
                <span className="bg-red-100 text-red-600 text-[10px] font-bold px-2 py-0.5 rounded-full border border-red-200">HIGH SEVERITY</span>
              </div>
              <h3 className="text-gray-900 font-bold text-base mb-2">Streetlight structure collapsed</h3>
              <div className="flex items-center gap-2 mb-4">
                <MapPin size={12} className="text-[#B85C2E]" />
                <span className="text-xs font-semibold text-gray-500">I-8/4, Islamabad Sector</span>
              </div>
              <div className="bg-gray-50 rounded-2xl p-4 flex items-center justify-between border border-gray-100">
                <div className="flex items-center gap-2">
                  <div className="bg-green-100 p-1.5 rounded-full text-green-600"><CheckCircle2 size={14} /></div>
                  <span className="text-xs font-bold text-gray-700">AI Validated</span>
                </div>
                <span className="text-xs font-black text-green-600">98% Confidence</span>
              </div>
            </div>

            {/* UI Mock: Analytics Metric */}
            <div className="bg-[#FDFDFD] rounded-3xl p-6 shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-white/10 backdrop-blur-md"
                 style={{ animation: 'float-slower 10s ease-in-out infinite' }}>
              <div className="flex gap-4 items-center">
                <div className="bg-amber-100 p-4 rounded-2xl text-amber-600 border border-amber-200">
                  <Activity size={24} />
                </div>
                <div>
                  <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Resolution Rate</p>
                  <p className="text-2xl font-black text-gray-900">84.2% <span className="text-xs font-bold text-green-500 bg-green-50 px-1.5 py-0.5 rounded-md ml-1 border border-green-100">↑ 12%</span></p>
                </div>
              </div>
            </div>

          </div>

        </div>

        {/* Footer */}
        <div className="p-12 relative z-20 mt-auto">
          <p className="text-[10px] font-bold text-white/20 uppercase tracking-widest">
            © 2025 StreetLight — Admin Portal
          </p>
        </div>
      </div>

      {/* ── Right panel (Form Theme) ── */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 lg:p-12 overflow-y-auto relative z-0">
        
        {/* Subtle grid pattern background */}
        <div className="absolute inset-0 z-[-1] opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#B85C2E 1.5px, transparent 1.5px)', backgroundSize: '32px 32px' }}></div>

        {/* Mobile logo */}
        <div className="lg:hidden flex items-center gap-2.5 mb-8">
          <img src="/logo.jpg" alt="StreetLight" className="w-10 h-10 rounded-xl object-cover shadow-sm bg-black" />
          <span className="font-black text-xl text-gray-900 tracking-tight">StreetLight</span>
        </div>

        {/* Desktop form container elements */}
        <div className="w-full max-w-[420px] flex flex-col items-center relative z-10">
          
          <div className="hidden lg:flex mb-8 items-center justify-center w-24 h-24 rounded-[30px] shadow-2xl shadow-[#B85C2E]/20 overflow-hidden bg-[#060913] border-[6px] border-white transition-transform hover:scale-105 duration-300 relative group">
             <div className="absolute inset-0 bg-[#B85C2E] opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
            <img src="/logo.jpg" alt="StreetLight" className="w-[85%] h-[85%] object-cover rounded-[20px]" />
          </div>

          <h2 className="text-4xl font-black text-gray-900 mb-3 tracking-tighter text-center">Welcome back</h2>
          <p className="text-sm text-gray-500 mb-10 text-center font-medium">Sign in to your municipal admin account</p>

          <form onSubmit={handleSignIn} className="bg-white/70 backdrop-blur-2xl rounded-[32px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white p-10 w-full flex flex-col gap-6 relative overflow-hidden">
            
            {/* Subtle glow rim inside form */}
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#B85C2E]/40 to-transparent"></div>

            <div className="flex flex-col gap-2">
              <label className="text-sm font-extrabold text-gray-700 ml-1">Email address</label>
              <div className="flex items-center gap-3 bg-gray-50/80 rounded-2xl px-4 h-14 border border-gray-200 transition-all duration-300 focus-within:bg-white focus-within:border-[#B85C2E] focus-within:ring-4 focus-within:ring-[#B85C2E]/10 focus-within:shadow-sm group">
                <Mail size={18} className="text-gray-400 group-focus-within:text-[#B85C2E] transition-colors shrink-0" />
                <input
                  type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="officer@streetlight.local"
                  className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none w-full font-medium"
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between ml-1">
                <label className="text-sm font-extrabold text-gray-700">Password</label>
               
              </div>
              <div className="flex items-center gap-3 bg-gray-50/80 rounded-2xl px-4 h-14 border border-gray-200 transition-all duration-300 focus-within:bg-white focus-within:border-[#B85C2E] focus-within:ring-4 focus-within:ring-[#B85C2E]/10 focus-within:shadow-sm group">
                <Lock size={18} className="text-gray-400 group-focus-within:text-[#B85C2E] transition-colors shrink-0" />
                <input
                  type={showPassword ? 'text' : 'password'} value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none w-full font-medium tracking-wider"
                  autoComplete="current-password"
                />
                <button type="button" onClick={() => setShowPassword(p => !p)} className="text-gray-400 hover:text-gray-700 transition-colors">
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 bg-red-50/80 border border-red-100 rounded-2xl px-4 py-3 animate-[fadeIn_0.2s_ease-out]">
                <span className="text-xs font-bold text-red-600">{error}</span>
              </div>
            )}

            <button
              type="submit" disabled={isLoading}
              className="w-full h-14 mt-4 rounded-2xl text-white font-extrabold text-[15px] tracking-wide transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_12px_25px_-5px_rgba(184,92,46,0.5)] active:scale-[0.98] disabled:opacity-60 disabled:hover:translate-y-0"
              style={{ backgroundColor: '#B85C2E', boxShadow: '0 6px 15px -3px rgba(184,92,46,0.3)' }}
            >
              {isLoading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <p className="mt-10 text-[11px] font-bold text-gray-400/80 text-center tracking-widest uppercase">
            StreetLight Civic Platform · Admin v2.0
          </p>
        </div>
      </div>
    </div>
  )
}

export default SignIn

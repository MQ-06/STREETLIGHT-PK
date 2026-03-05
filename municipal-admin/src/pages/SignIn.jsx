import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Eye, EyeOff, Users, ChevronDown } from 'lucide-react'

function SignIn() {
  const [showPassword, setShowPassword] = useState(false)
  const [role, setRole] = useState('citizen')
  const navigate = useNavigate()

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
        <button
          className="w-9 h-9 rounded-full flex items-center justify-center text-base"
          style={{ backgroundColor: '#2d2d2d', color: '#fff' }}
        >
          🌙
        </button>
      </header>

      {/* MAIN */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">

        {/* Icon circle */}
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
          Manage your city reports and impact from your dashboard.
        </p>

        {/* FORM CARD */}
        <div className="bg-white rounded-3xl shadow-md px-8 py-6 w-full max-w-md flex flex-col gap-4">

          {/* Email */}
          <div className="flex flex-col gap-1">
            <label className="text-sm font-semibold text-gray-800">Email Address</label>
            <div className="flex items-center gap-3 bg-gray-100 rounded-full px-4 py-2.5">
              <Mail size={15} className="text-gray-400 shrink-0" />
              <input
                type="email"
                placeholder="john.doe@city.com"
                className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
              />
            </div>
          </div>

          {/* Password */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-gray-800">Password</label>
              <a href="#" className="text-sm font-medium" style={{ color: '#b85c2a' }}>
                Forgot password?
              </a>
            </div>
            <div className="flex items-center gap-3 bg-gray-100 rounded-full px-4 py-2.5">
              <Lock size={15} className="text-gray-400 shrink-0" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          {/* Account Role */}
          <div className="flex flex-col gap-1">
            <label className="text-sm font-semibold text-gray-800">Account Role</label>
            <div className="relative flex items-center bg-gray-100 rounded-full px-4 py-2.5">
              <Users size={15} className="text-gray-400 shrink-0 mr-3" />
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="flex-1 bg-transparent text-sm text-gray-700 outline-none appearance-none cursor-pointer"
              >
                <option value="citizen">Citizen User</option>
                <option value="municipal">Municipal Officer</option>
                <option value="admin">Administrator</option>
              </select>
              <ChevronDown size={15} className="text-gray-400 absolute right-4 pointer-events-none" />
            </div>
          </div>

          {/* Sign In Button */}
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full py-3 rounded-full text-white font-semibold text-sm tracking-wide transition hover:opacity-90 active:scale-95"
            style={{ backgroundColor: '#b85c2a' }}
          >
            Sign In
          </button>

          {/* Create Account */}
          <p className="text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <a href="#" className="font-bold" style={{ color: '#b85c2a' }}>
              Create Account
            </a>
          </p>

        </div>
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
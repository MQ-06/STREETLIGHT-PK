import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'

function InputField({ label, type = 'text', placeholder, icon: Icon }) {
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-semibold text-gray-800">{label}</label>
      )}
      <div className="flex items-center gap-3 bg-gray-100 rounded-full px-4 py-3">
        {Icon && <Icon size={16} className="text-gray-400 shrink-0" />}
        <input
          type={inputType}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none"
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-gray-400 hover:text-gray-600"
          >
            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}
      </div>
    </div>
  )
}

export default InputField

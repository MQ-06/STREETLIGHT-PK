import { Users, ChevronDown } from 'lucide-react'

function SelectField({ label, options = [], defaultValue }) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-semibold text-gray-800">{label}</label>
      )}
      <div className="relative flex items-center bg-gray-100 rounded-full px-4 py-3">
        <Users size={16} className="text-gray-400 shrink-0 mr-3" />
        <select
          defaultValue={defaultValue}
          className="flex-1 bg-transparent text-sm text-gray-700 outline-none appearance-none cursor-pointer"
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown size={16} className="text-gray-400 absolute right-4 pointer-events-none" />
      </div>
    </div>
  )
}

export default SelectField

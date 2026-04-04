import { SEVERITY_MAP } from '../utils/theme'

/**
 * SeverityBadge — colored pill for issue severity.
 * Props: severity (string: 'large'|'medium'|'small'|'high'|'low')
 */
export default function SeverityBadge({ severity }) {
  const key = (severity || 'small').toLowerCase()
  const s   = SEVERITY_MAP[key] || SEVERITY_MAP['small']

  return (
    <span
      className="inline-block text-xs font-bold px-2.5 py-1 rounded-full"
      style={{ backgroundColor: s.bg, color: s.text }}
    >
      {s.label}
    </span>
  )
}

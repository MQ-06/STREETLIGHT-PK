// Module 3 — single AI insight card (warm beige design system)
const ACCENT = {
  forecast:   { border: '#E5701F', bg: '#FFF7F3', icon: null },
  bottleneck: { border: '#F59E0B', bg: '#FFFBEB', icon: '⚠' },
  health:     { border: '#22C55E', bg: '#F0FDF4', icon: '✦' },
  critical:   { border: '#EF4444', bg: '#FEF2F2', icon: '⚠' },
}

const DIRECTION_ICON = { up: '↑', down: '↓', stable: '→' }
const DIRECTION_COLOR = {
  up:     '#DC2626',   // more reports = bad
  down:   '#15803D',   // fewer = good
  stable: '#6B7280',
}

export function AIInsightCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3 animate-pulse">
      <div className="h-3 w-28 bg-gray-100 rounded" />
      <div className="h-9 w-20 bg-gray-100 rounded" />
      <div className="h-4 w-36 bg-gray-100 rounded" />
    </div>
  )
}

export default function AIInsightCard({ type, value, label, sub, direction }) {
  // Choose accent variant
  let variant = type
  if (type === 'health' && sub === 'Critical') variant = 'critical'

  const { border, bg, icon } = ACCENT[variant] || ACCENT.health

  return (
    <div
      className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-1 relative overflow-hidden"
      style={{ borderLeft: `4px solid ${border}` }}
    >
      {/* Subtle tinted corner patch */}
      <div
        className="absolute top-0 right-0 w-16 h-16 rounded-bl-full opacity-40"
        style={{ backgroundColor: bg }}
      />

      {/* Top icon */}
      {icon && (
        <span className="text-lg leading-none" style={{ color: border }}>{icon}</span>
      )}

      {/* Label */}
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}</p>

      {/* Main value */}
      <div className="flex items-end gap-2 mt-1">
        <span className="text-3xl font-black text-gray-900 leading-none">{value}</span>

        {/* Direction badge (forecast only) */}
        {direction && (
          <span
            className="text-sm font-bold mb-0.5"
            style={{ color: DIRECTION_COLOR[direction] }}
          >
            {DIRECTION_ICON[direction]}
          </span>
        )}
      </div>

      {/* Sub-text */}
      {sub && (
        <p className="text-xs text-gray-500 mt-0.5">{sub}</p>
      )}
    </div>
  )
}

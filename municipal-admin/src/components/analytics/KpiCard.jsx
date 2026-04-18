// Module 1 — KPI stat card (warm beige design system)
const SIGNAL_PILL = {
  green: { bg: '#F0FDF4', text: '#15803D' },
  amber: { bg: '#FFFBEB', text: '#B45309' },
  red:   { bg: '#FEF2F2', text: '#DC2626' },
}

const ICONS = {
  warn:  <span title="Warning" style={{ color: '#DC2626', fontSize: 16 }}>⚠</span>,
  check: <span title="Good"    style={{ color: '#22C55E', fontSize: 16 }}>✓</span>,
}

// Skeleton block shown while data loads
export function KpiCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-3 animate-pulse">
      <div className="h-3 w-24 bg-gray-100 rounded" />
      <div className="h-8 w-20 bg-gray-100 rounded" />
      <div className="h-5 w-16 bg-gray-100 rounded-full" />
    </div>
  )
}

export default function KpiCard({ label, value, delta, icon }) {
  const pill = delta ? SIGNAL_PILL[delta.color] || SIGNAL_PILL.green : null

  return (
    <div className="bg-white rounded-2xl border border-warm-border p-5 flex flex-col gap-2 relative">
      {/* Top-right icon */}
      {icon && (
        <span className="absolute top-4 right-4">{ICONS[icon]}</span>
      )}

      {/* Label */}
      <p className="text-xs font-medium text-gray-400 uppercase tracking-wide">{label}:</p>

      {/* Value + delta on same line */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-3xl font-black text-gray-900 leading-none">{value ?? '—'}</span>
        {delta && (
          <span
            className="text-xs font-bold px-2 py-0.5 rounded-full"
            style={{ backgroundColor: pill.bg, color: pill.text }}
          >
            {delta.text}
          </span>
        )}
      </div>
    </div>
  )
}

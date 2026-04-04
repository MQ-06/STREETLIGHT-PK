/**
 * StatCard — reusable KPI tile used on all 3 dashboards.
 *
 * Props:
 *   label      string   — metric name
 *   value      string   — formatted value (e.g. "1,284" or "—")
 *   badge      string   — small top-right chip text (e.g. "+12.4%" or "High")
 *   badgeColor string   — chip text color (hex)
 *   badgeBg    string   — chip background color (hex) optional
 *   icon       ReactNode— lucide icon element
 *   iconBg     string   — icon wrapper background
 *   iconColor  string   — icon color
 *   dark       bool     — filled primary variant (Resolved card)
 *   barWidth   string   — CSS width for progress bar (e.g. "60%")
 *   barColor   string   — progress bar fill color
 *   loading    bool     — show skeleton shimmer
 *   onClick    fn       — optional click handler
 */
export default function StatCard({
  label, value = '—', badge, badgeColor, badgeBg,
  icon, iconBg, iconColor,
  dark = false, barWidth = '0%', barColor,
  loading = false, onClick,
}) {
  const cardStyle = dark
    ? { backgroundColor: '#B85C2E', color: '#fff' }
    : { backgroundColor: '#fff', color: '#111827' }

  const subColor = dark ? 'rgba(255,255,255,0.7)' : '#9CA3AF'
  const trackBg  = dark ? 'rgba(255,255,255,0.2)' : '#F3F4F6'

  return (
    <div
      className={`group rounded-3xl p-6 flex flex-col gap-3 shadow-sm border transition-all duration-300
        ${dark ? 'border-transparent shadow-primary/20 hover:shadow-primary/40 hover:-translate-y-1' : 'border-warm-border hover:border-[#B85C2E]/20 hover:shadow-lg hover:-translate-y-1'}
        ${onClick ? 'cursor-pointer' : ''}`}
      style={cardStyle}
      onClick={onClick}
    >
      {/* Top row */}
      <div className="flex items-start justify-between">
        <div
          className="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0"
          style={{ backgroundColor: iconBg || 'rgba(255,255,255,0.2)' }}
        >
          <span style={{ color: iconColor || '#fff', display: 'flex' }}>
            {icon}
          </span>
        </div>

        {badge && (
          <span
            className="text-xs font-bold px-2 py-1 rounded-lg"
            style={{
              color:           badgeColor || '#22C55E',
              backgroundColor: badgeBg   || (dark ? 'rgba(255,255,255,0.15)' : '#F0FDF4'),
            }}
          >
            {badge}
          </span>
        )}
      </div>

      {/* Value */}
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: subColor }}>
          {label}
        </p>
        {loading
          ? <div className="h-8 w-24 rounded-lg animate-pulse" style={{ backgroundColor: dark ? 'rgba(255,255,255,0.2)' : '#F3F4F6' }} />
          : <p className="text-3xl font-black">{value}</p>
        }
      </div>

      {/* Progress bar */}
      <div className="h-1 w-full rounded-full" style={{ backgroundColor: trackBg }}>
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: loading ? '0%' : barWidth, backgroundColor: barColor || (dark ? 'rgba(255,255,255,0.5)' : '#B85C2E') }}
        />
      </div>
    </div>
  )
}

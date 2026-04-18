/**
 * ViewModeToggle — M8a: Floating top-center view mode pill bar
 *
 * Props:
 *   viewMode    — 'heatmap' | 'pin' | 'both'
 *   setViewMode — (value) => void
 */

const PILLS = [
  { value: 'heatmap', label: 'Heatmap View' },
  { value: 'pin',     label: 'Pin View'     },
  { value: 'both',    label: 'Both'         },
]

export default function ViewModeToggle({ viewMode, setViewMode }) {
  return (
    <div style={{
      display:      'inline-flex',
      background:   '#FFFFFF',
      borderRadius: 24,
      padding:      4,
      boxShadow:    '0 2px 8px rgba(0,0,0,0.15)',
      gap:          2,
    }}>
      {PILLS.map(({ value, label }) => {
        const active = viewMode === value
        return (
          <button
            key={value}
            onClick={() => setViewMode(value)}
            style={{
              background:   active ? '#E8612D' : 'transparent',
              color:        active ? '#FFFFFF' : '#64748B',
              border:       'none',
              borderRadius: 20,
              padding:      '7px 16px',
              fontSize:     13,
              fontWeight:   active ? 700 : 500,
              cursor:       'pointer',
              whiteSpace:   'nowrap',
              transition:   'background 0.15s, color 0.15s',
              display:      'flex',
              alignItems:   'center',
              gap:          5,
            }}
            onMouseEnter={e => { if (!active) e.currentTarget.style.background = '#F3F4F6' }}
            onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent' }}
          >
            {active && value === 'heatmap' && (
              <span style={{ fontSize: 11 }}>⚠</span>
            )}
            {label}
          </button>
        )
      })}
    </div>
  )
}

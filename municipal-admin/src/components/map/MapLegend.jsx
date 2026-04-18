/**
 * MapLegend — M5a: Bottom-right floating legend card
 *
 * Props:
 *   reports — filtered report array from useMapReports
 *
 * Shows counts for each pin colour category.
 */

const C = {
  bg:     '#111A2E',
  border: '#1C2A45',
  text:   '#E2E8F0',
  muted:  '#64748B',
}

const ROWS = [
  {
    color: '#EF4444',
    label: 'High Severity Pending',
    match: r => {
      const sev   = (r.severity || r.ai_severity || '').toLowerCase()
      const stage = (r.kanban_stage || '').toUpperCase()
      return sev === 'large' && stage !== 'RESOLVED'
    },
  },
  {
    color: '#F97316',
    label: 'In Progress',
    match: r => (r.kanban_stage || '').toUpperCase() === 'IN_PROGRESS',
  },
  {
    color: '#22C55E',
    label: 'Resolved',
    match: r => (r.kanban_stage || '').toUpperCase() === 'RESOLVED',
  },
  {
    color: '#3B82F6',
    label: 'New Reports',
    match: r => (r.kanban_stage || '').toUpperCase() === 'NEW',
  },
]

export default function MapLegend({ reports = [] }) {
  return (
    <div style={{
      background:   C.bg,
      border:       `1px solid ${C.border}`,
      borderRadius: 12,
      padding:      '10px 14px',
    }}>
      <p style={{ margin: '0 0 8px', fontSize: 13, fontWeight: 700, color: C.text }}>
        Reports
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {ROWS.map(({ color, label, match }) => {
          const count = reports.filter(match).length
          return (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                width: 10, height: 10,
                borderRadius: '50%',
                background: color,
                flexShrink: 0,
                display: 'inline-block',
              }} />
              <span style={{ fontSize: 11, color: C.text }}>
                {label} ({count})
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

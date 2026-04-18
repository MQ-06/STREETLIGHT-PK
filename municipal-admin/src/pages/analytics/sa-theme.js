// Super Admin dark navy design tokens
export const SA = {
  bg:       '#0B1120',
  card:     '#111A2E',
  border:   '#1C2A45',
  text:     '#E2E8F0',
  muted:    '#64748B',
  orange:   '#E8612D',
  green:    '#22C55E',
  red:      '#EF4444',
  amber:    '#F59E0B',
  blue:     '#3B82F6',

  // Card style shorthand (inline-style objects)
  cardStyle:   { background: '#111A2E', border: '1px solid #1C2A45', borderRadius: 16 },
  borderStyle: { borderColor: '#1C2A45' },
}

// Signal → colour mapping (KPI deltas, status badges)
export function signalColor(signal) {
  if (signal === 'good')    return SA.green
  if (signal === 'warn')    return SA.amber
  if (signal === 'bad')     return SA.red
  return SA.muted
}

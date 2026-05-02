/**
 * ActiveAlertsCard — M4: Floating top-right viewport stats card
 *
 * Props:
 *   reports   — full filtered report array from useMapReports
 *   mapBounds — Leaflet LatLngBounds object (updated on map move)
 *
 * Filters reports to the current viewport using bounds.contains(),
 * then derives area name, unresolved count, and hotspot location.
 */

// ── Design tokens ─────────────────────────────────────────────────────────────
const C = {
  bg:     '#111A2E',
  border: '#1C2A45',
  text:   '#E2E8F0',
  muted:  '#64748B',
  orange: '#E8612D',
}

function capitalize(str) {
  if (!str) return '—'
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/** Reports visible inside the current map viewport */
function inBounds(reports, mapBounds) {
  if (!mapBounds) return reports
  return reports.filter(r => {
    if (r.lat == null || r.lng == null) return false
    try { return mapBounds.contains([r.lat, r.lng]) } catch { return false }
  })
}

/** Most common value of a string field in an array */
function mostCommon(arr, key) {
  if (!arr.length) return null
  const counts = {}
  arr.forEach(r => { const v = r[key]; if (v) counts[v] = (counts[v] || 0) + 1 })
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null
}

export default function ActiveAlertsCard({ reports = [], mapBounds }) {
  const visible    = inBounds(reports, mapBounds)
  const unresolved = visible.filter(r => {
    const s = (r.kanban_stage || '').toUpperCase()
    return s !== 'RESOLVED' && s !== 'CLOSED'
  })

  const areaName = capitalize(mostCommon(visible, 'assigned_city'))
  const hotspot  = capitalize(mostCommon(unresolved, 'assigned_city'))

  return (
    <div style={{
      background:   C.bg,
      border:       `1px solid ${C.border}`,
      borderRadius: 12,
      padding:      '12px 16px',
      minWidth:     220,
      zIndex:       1000,
    }}>
      {/* Title */}
      <p style={{
        margin:     '0 0 10px',
        fontSize:   13,
        fontWeight: 700,
        color:      C.text,
        whiteSpace: 'nowrap',
      }}>
        Active Alerts&nbsp;
        <span style={{ color: C.muted, fontWeight: 400 }}>| {areaName}</span>
      </p>

      {/* Stats row */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>

        <StatRow label="Total Visible" value={visible.length} valueColor={C.text} />
        <StatRow label="Unresolved"    value={unresolved.length} valueColor={C.orange} />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: C.muted }}>Hotspot Location</span>
          <span style={{ fontSize: 11, color: C.muted, fontWeight: 600 }}>{hotspot}</span>
        </div>

      </div>
    </div>
  )
}

function StatRow({ label, value, valueColor }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: 11, color: C.muted }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 700, color: valueColor }}>{value}</span>
    </div>
  )
}

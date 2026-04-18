/**
 * MapPins — M3a: Colored DivIcon markers
 *
 * Props:
 *   reports    — filtered report array from useMapReports
 *   onPinClick — (report) => void  opens M6 detail panel
 */
import { useMemo } from 'react'
import { Marker, Tooltip } from 'react-leaflet'
import L from 'leaflet'

// ── Stage → color map ─────────────────────────────────────────────────────────
const STAGE_COLOR = {
  NEW:                  '#3B82F6',   // blue
  PENDING_VERIFICATION: '#F97316',   // orange
  VERIFIED:             '#F97316',
  IN_PROGRESS:          '#F97316',
  AWAITING_FEEDBACK:    '#F97316',
  RESOLVED:             '#22C55E',   // green
}
const DEFAULT_COLOR = '#EF4444'    // red (fallback / high-severity override)

function pinColor(report) {
  const stage    = (report.kanban_stage || '').toUpperCase()
  const severity = (report.ai_severity  || report.severity || '').toLowerCase()

  // High-severity unresolved reports → red
  if (severity === 'large' && stage !== 'RESOLVED') return DEFAULT_COLOR

  return STAGE_COLOR[stage] || DEFAULT_COLOR
}

function makeDivIcon(color) {
  return L.divIcon({
    className: '',   // suppress Leaflet's default white square
    html: `<div style="
      width:         14px;
      height:        14px;
      border-radius: 50%;
      background:    ${color};
      border:        2px solid white;
      box-shadow:    0 2px 6px rgba(0,0,0,0.4);
    "></div>`,
    iconSize:   [14, 14],
    iconAnchor: [7, 7],
  })
}

export default function MapPins({ reports = [], onPinClick }) {
  // Pre-build icons keyed by color so we don't recreate on every render
  const iconCache = useMemo(() => {
    const cache = {}
    const colors = new Set(reports.map(pinColor))
    colors.forEach(c => { cache[c] = makeDivIcon(c) })
    return cache
  }, [reports])

  return reports.map(report => {
    const lat = report.lat
    const lng = report.lng
    if (lat == null || lng == null) return null

    const color   = pinColor(report)
    const icon    = iconCache[color] || makeDivIcon(color)
    const label   = `${report.category || 'Report'} ${report.display_id || ''}`

    return (
      <Marker
        key={report.id}
        position={[lat, lng]}
        icon={icon}
        eventHandlers={{ click: () => onPinClick(report) }}
      >
        <Tooltip direction="top" offset={[0, -10]} opacity={0.92}>
          <span style={{ fontSize: 12, fontWeight: 600 }}>{label}</span>
        </Tooltip>
      </Marker>
    )
  })
}

/**
 * ClusterLayer — M8b: MarkerCluster layer with dark navy bubbles + trend arrows
 *
 * Props:
 *   reports        — filtered report array
 *   onClusterClick — (cluster) => void  (M9 hook-in)
 *
 * Must render inside <MapContainer>.
 */
import { useEffect, useRef } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.markercluster'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

// ── Reuse pin-color logic from M3a ────────────────────────────────────────────
const STAGE_COLOR = {
  NEW:                  '#3B82F6',
  PENDING_VERIFICATION: '#F97316',
  VERIFIED:             '#F97316',
  IN_PROGRESS:          '#F97316',
  AWAITING_FEEDBACK:    '#F97316',
  RESOLVED:             '#22C55E',
}

function pinColor(report) {
  const stage    = (report.kanban_stage || '').toUpperCase()
  const severity = (report.ai_severity || report.severity || '').toLowerCase()
  if (severity === 'large' && stage !== 'RESOLVED') return '#EF4444'
  return STAGE_COLOR[stage] || '#EF4444'
}

function makeChildIcon(report) {
  const color = pinColor(report)
  return L.divIcon({
    className: '',
    html: `<div style="
      width:14px;height:14px;border-radius:50%;
      background:${color};border:2px solid white;
      box-shadow:0 2px 6px rgba(0,0,0,0.4);
    "></div>`,
    iconSize:   [14, 14],
    iconAnchor: [7, 7],
  })
}

// ── Trend calculation ─────────────────────────────────────────────────────────
const NOW          = Date.now()
const ONE_WEEK_MS  = 7  * 24 * 60 * 60 * 1000
const TWO_WEEKS_MS = 14 * 24 * 60 * 60 * 1000

function trendArrow(reports) {
  const thisWeek = reports.filter(r => {
    const t = r.created_at ? new Date(r.created_at).getTime() : 0
    return t >= NOW - ONE_WEEK_MS
  }).length

  const lastWeek = reports.filter(r => {
    const t = r.created_at ? new Date(r.created_at).getTime() : 0
    return t >= NOW - TWO_WEEKS_MS && t < NOW - ONE_WEEK_MS
  }).length

  if (thisWeek > lastWeek) return { arrow: '↑', color: '#EF4444' }
  if (thisWeek < lastWeek) return { arrow: '↓', color: '#22C55E' }
  return { arrow: '→', color: '#64748B' }
}

// ── Cluster icon factory ──────────────────────────────────────────────────────
function clusterIcon(cluster) {
  const markers = cluster.getAllChildMarkers()
  const reports = markers.map(m => m._report).filter(Boolean)
  const count   = cluster.getChildCount()
  const { arrow, color: arrowColor } = trendArrow(reports)

  const size = count >= 50 ? 60 : count >= 20 ? 52 : 44

  return L.divIcon({
    className: '',
    html: `<div style="
      background:#111A2E;border:3px solid white;border-radius:50%;
      width:${size}px;height:${size}px;
      display:flex;flex-direction:column;
      align-items:center;justify-content:center;
      color:white;box-shadow:0 2px 8px rgba(0,0,0,0.3);
    ">
      <span style="font-weight:700;font-size:14px;line-height:1.1;">${count}</span>
      <span style="font-size:10px;color:${arrowColor};line-height:1;">${arrow}</span>
    </div>`,
    iconSize:   [size, size],
    iconAnchor: [size / 2, size / 2],
  })
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ClusterLayer({ reports = [], onClusterClick }) {
  const map      = useMap()
  const groupRef = useRef(null)

  useEffect(() => {
    // Create cluster group once
    if (!groupRef.current) {
      groupRef.current = L.markerClusterGroup({
        iconCreateFunction: clusterIcon,
        showCoverageOnHover: false,
        spiderfyOnMaxZoom:   true,
        maxClusterRadius:    60,
        // Suppress default styles — we use fully custom DivIcons
        polygonOptions: { opacity: 0, fillOpacity: 0 },
      })

      groupRef.current.on('clusterclick', (e) => {
        const cluster  = e.layer
        const childCnt = cluster.getChildCount()
        const atMax    = map.getZoom() >= map.getMaxZoom()

        if (atMax || childCnt < 100) {
          onClusterClick?.(cluster)
        }
        // Otherwise markercluster's default zoom-in fires automatically
      })

      map.addLayer(groupRef.current)
    }

    return () => {
      if (groupRef.current) {
        map.removeLayer(groupRef.current)
        groupRef.current = null
      }
    }
  }, [map]) // eslint-disable-line react-hooks/exhaustive-deps

  // Sync markers whenever reports change
  useEffect(() => {
    if (!groupRef.current) return

    groupRef.current.clearLayers()

    reports.forEach(report => {
      if (report.lat == null || report.lng == null) return

      const marker = L.marker([report.lat, report.lng], {
        icon: makeChildIcon(report),
      })
      // Attach report data for trend calculation in iconCreateFunction
      marker._report = report
      groupRef.current.addLayer(marker)
    })
  }, [reports])

  return null
}

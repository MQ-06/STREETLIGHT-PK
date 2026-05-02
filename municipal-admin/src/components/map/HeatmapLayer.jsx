/**
 * HeatmapLayer — M3b: Gaussian heatmap via leaflet.heat
 *
 * Props:
 *   reports — filtered report array (excludes terminal RESOLVED/CLOSED)
 *
 * Rendered inside <MapContainer> so useMap() works.
 */
import { useEffect, useRef } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'

const SEVERITY_WEIGHT = { large: 1.0, medium: 0.6, small: 0.3 }

const HEAT_OPTIONS = {
  radius:  25,
  blur:    15,
  maxZoom: 17,
  gradient: {
    0.2: 'blue',
    0.4: 'cyan',
    0.6: 'yellow',
    0.8: 'orange',
    1.0: 'red',
  },
}

export default function HeatmapLayer({ reports = [] }) {
  const map      = useMap()
  const layerRef = useRef(null)

  useEffect(() => {
    // Build points from non-terminal reports only
    const points = reports
      .filter(r => {
        const stage = (r.kanban_stage || '').toUpperCase()
        return stage !== 'RESOLVED' && stage !== 'CLOSED' && r.lat != null && r.lng != null
      })
      .map(r => {
        const sev    = (r.ai_severity || r.severity || 'medium').toLowerCase()
        const weight = SEVERITY_WEIGHT[sev] ?? 0.6
        return [r.lat, r.lng, weight]
      })

    // Remove existing layer if any
    if (layerRef.current) {
      map.removeLayer(layerRef.current)
    }

    if (points.length === 0) return

    layerRef.current = L.heatLayer(points, HEAT_OPTIONS).addTo(map)

    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current)
        layerRef.current = null
      }
    }
  }, [map, reports])

  return null
}

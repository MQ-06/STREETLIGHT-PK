/**
 * HotspotMap — M1: Dark Map Shell
 *
 * Renders inside Layout.jsx (Sidebar + Topbar already provided).
 * Fills the <main> area with:
 *   - 280px left FilterSidebar (M2)
 *   - Leaflet map (CartoDB DarkMatter) taking remaining space
 *   - Floating overlays: top-right ActiveAlertsCard (M4),
 *                        bottom-right MapLegend (M5),
 *                        bottom-center ViewportLabel (M5)
 *   - Right-edge ReportDetailPanel slide-in on pin click (M6)
 */
import { useState, useCallback } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

import useMapReports         from '../../hooks/useMapReports'
import FilterSidebar         from '../../components/map/FilterSidebar'
import ActiveAlertsCard      from '../../components/map/ActiveAlertsCard'
import MapLegend             from '../../components/map/MapLegend'
import ViewportLabel         from '../../components/map/ViewportLabel'
import ReportDetailPanel     from '../../components/map/ReportDetailPanel'
import MapPins               from '../../components/map/MapPins'
import HeatmapLayer          from '../../components/map/HeatmapLayer'
import MapBoundsTracker      from '../../components/map/MapBoundsTracker'

// ── Design tokens ─────────────────────────────────────────────────────────────
const C = {
  bg:     '#0B1120',
  panel:  '#111A2E',
  border: '#1C2A45',
  text:   '#E2E8F0',
  muted:  '#64748B',
  orange: '#E8612D',
}

// ── CartoDB DarkMatter tile URL ───────────────────────────────────────────────
const DARK_TILE = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_ATTR = '&copy; <a href="https://carto.com/">CARTO</a>'

// ── Default map view — centred on Lahore ──────────────────────────────────────
const DEFAULT_CENTER = [31.5204, 74.3587]
const DEFAULT_ZOOM   = 12

const SIDEBAR_W = 280   // px

export default function HotspotMap() {
  const { allReports, filtered, loading, error, filters, setFilter } = useMapReports()
  const [selectedReport, setSelectedReport] = useState(null)
  const [mapBounds,      setMapBounds]      = useState(null)
  const onBoundsChange = useCallback(b => setMapBounds(b), [])

  return (
    /*
     * h-full fills the <main> area provided by Layout.
     * overflow-hidden prevents Layout's overflow-y-auto from
     * adding a scrollbar around the map.
     */
    <div
      style={{
        display:    'flex',
        height:     '100%',
        overflow:   'hidden',
        background: C.bg,
      }}
    >
      {/* ── Left: Filter Sidebar (M2) ── */}
      <div
        style={{
          width:          SIDEBAR_W,
          flexShrink:     0,
          background:     C.panel,
          borderRight:    `1px solid ${C.border}`,
          display:        'flex',
          flexDirection:  'column',
          overflow:       'hidden',
        }}
      >
        {/* Sidebar header */}
        <div
          style={{
            padding:      '16px 20px',
            borderBottom: `1px solid ${C.border}`,
            display:      'flex',
            alignItems:   'center',
            gap:          10,
          }}
        >
          <span style={{ fontSize: 16 }}>📍</span>
          <div>
            <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: C.text }}>
              Hotspot Map
            </p>
            <p style={{ margin: 0, fontSize: 11, color: C.muted }}>
              {loading ? 'Loading…' : `${filtered.length} reports visible`}
            </p>
          </div>
        </div>

        {/* M2 Filter Sidebar content */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <FilterSidebar
            filters={filters}
            setFilter={setFilter}
            recentReports={filtered}
            onReportClick={setSelectedReport}
          />
        </div>
      </div>

      {/* ── Right: Map area ── */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>

        {/* Leaflet map — fills entire right area */}
        <MapContainer
          center={DEFAULT_CENTER}
          zoom={DEFAULT_ZOOM}
          style={{ width: '100%', height: '100%' }}
          zoomControl
        >
          <TileLayer url={DARK_TILE} attribution={TILE_ATTR} />

          {/* M3 — Heatmap + Pin markers */}
          <HeatmapLayer reports={filtered} />
          <MapPins reports={filtered} onPinClick={setSelectedReport} />

          {/* M4 — Tracks viewport bounds for ActiveAlertsCard */}
          <MapBoundsTracker onBoundsChange={onBoundsChange} />
        </MapContainer>

        {/* ── Floating overlays ── */}

        {/* Top-right: Active Alerts Card (M4) */}
        <div
          style={{
            position:   'absolute',
            top:        16,
            right:      selectedReport ? 376 : 16,
            zIndex:     900,
            transition: 'right 0.25s ease',
          }}
        >
          <ActiveAlertsCard reports={filtered} mapBounds={mapBounds} />
        </div>

        {/* Bottom-right: Map Legend (M5) */}
        <div
          style={{
            position:   'absolute',
            bottom:     16,
            right:      selectedReport ? 376 : 16,
            zIndex:     900,
            transition: 'right 0.25s ease',
          }}
        >
          <MapLegend />
        </div>

        {/* Bottom-center: Viewport Label (M5) */}
        <div
          style={{
            position:  'absolute',
            bottom:    16,
            left:      '50%',
            transform: 'translateX(-50%)',
            zIndex:    900,
          }}
        >
          <ViewportLabel count={filtered.length} />
        </div>

        {/* Loading overlay */}
        {loading && (
          <div
            style={{
              position:       'absolute',
              inset:          0,
              background:     'rgba(11,17,32,0.6)',
              display:        'flex',
              alignItems:     'center',
              justifyContent: 'center',
              zIndex:         800,
            }}
          >
            <p style={{ color: C.muted, fontSize: 14 }}>Loading reports…</p>
          </div>
        )}

        {/* Error overlay */}
        {error && (
          <div
            style={{
              position:       'absolute',
              inset:          0,
              background:     'rgba(11,17,32,0.7)',
              display:        'flex',
              alignItems:     'center',
              justifyContent: 'center',
              zIndex:         800,
            }}
          >
            <p style={{ color: '#EF4444', fontSize: 14 }}>{error}</p>
          </div>
        )}

        {/* ── M6: Report Detail Slide-in Panel ── */}
        <ReportDetailPanel
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />

      </div>
    </div>
  )
}

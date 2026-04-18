/**
 * HotspotMap — Hotspot Map shell (M1–M8)
 *
 * Renders inside Layout.jsx (Sidebar + Topbar already provided).
 * Fills the <main> area with:
 *   - 280px left FilterSidebar (M2)
 *   - Leaflet map (CartoDB DarkMatter) taking remaining space
 *   - Floating overlays: top-center ViewModeToggle (M8),
 *                        top-right ActiveAlertsCard (M4),
 *                        bottom-right MapLegend (M5),
 *                        bottom-center ViewportLabel (M5)
 *   - Right-edge ReportDetailPanel slide-in on pin click (M6)
 *
 * viewMode controls which layers render:
 *   'heatmap' → HeatmapLayer + ClusterLayer
 *   'pin'     → MapPins only
 *   'both'    → all three layers
 */
import { useState, useCallback, useRef } from 'react'
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
import ViewModeToggle        from '../../components/map/ViewModeToggle'
import ClusterLayer          from '../../components/map/ClusterLayer'
import ClusterPopup          from '../../components/map/ClusterPopup'

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
  const [mapCenter,      setMapCenter]      = useState(null)
  const [viewMode,       setViewMode]       = useState('both')
  const [activeCluster,  setActiveCluster]  = useState(null)   // { cluster, reports }
  const mapContainerRef = useRef(null)

  const onBoundsChange = useCallback(b => setMapBounds(b), [])
  const onCenterChange = useCallback(c => setMapCenter(c), [])

  const showHeatmap  = viewMode === 'heatmap' || viewMode === 'both'
  const showPins     = viewMode === 'pin'     || viewMode === 'both'
  const showClusters = viewMode === 'heatmap' || viewMode === 'both'

  return (
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
          width:         SIDEBAR_W,
          flexShrink:    0,
          background:    C.panel,
          borderRight:   `1px solid ${C.border}`,
          display:       'flex',
          flexDirection: 'column',
          overflow:      'hidden',
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
          <div style={{ flex: 1 }}>
            <p style={{ margin: 0, fontSize: 14, fontWeight: 700, color: C.text }}>
              Hotspot Map
            </p>
            <p style={{ margin: 0, fontSize: 11, color: C.muted }}>
              {loading ? 'Loading…' : `${filtered.length} reports visible`}
            </p>
          </div>
          {/* Export/download snapshot */}
          <button
            title="Export map snapshot"
            onClick={() => window.print()}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              color: C.muted, fontSize: 16, padding: 4, lineHeight: 1,
              flexShrink: 0,
            }}
            onMouseEnter={e => e.currentTarget.style.color = C.orange}
            onMouseLeave={e => e.currentTarget.style.color = C.muted}
          >
            ⬇
          </button>
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

          {/* M3a — Individual pin markers (pin + both modes) */}
          {showPins && (
            <MapPins reports={filtered} onPinClick={setSelectedReport} />
          )}

          {/* M3b — Gaussian heatmap (heatmap + both modes) */}
          {showHeatmap && (
            <HeatmapLayer reports={filtered} />
          )}

          {/* M8b — Cluster layer (heatmap + both modes) */}
          {showClusters && (
            <ClusterLayer
              reports={filtered}
              onClusterClick={(cluster, clusterReports) =>
                setActiveCluster({ cluster, reports: clusterReports })
              }
            />
          )}

          {/* M9 — Cluster popup */}
          {activeCluster && (
            <ClusterPopup
              cluster={activeCluster.cluster}
              reports={activeCluster.reports}
              onQuickView={report => {
                setSelectedReport(report)
                setActiveCluster(null)
              }}
              onClose={() => setActiveCluster(null)}
            />
          )}

          {/* M4/M5 — Tracks viewport bounds and center */}
          <MapBoundsTracker onBoundsChange={onBoundsChange} onCenterChange={onCenterChange} />
        </MapContainer>

        {/* ── Floating overlays ── */}

        {/* Top-center: View Mode Toggle (M8a) */}
        <div
          style={{
            position:  'absolute',
            top:       16,
            left:      '50%',
            transform: 'translateX(-50%)',
            zIndex:    1000,
          }}
        >
          <ViewModeToggle viewMode={viewMode} setViewMode={setViewMode} />
        </div>

        {/* Top-right: Active Alerts Card (M4) */}
        <div
          style={{
            position:   'absolute',
            top:        16,
            right:      selectedReport ? 396 : 16,
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
            right:      selectedReport ? 396 : 16,
            zIndex:     900,
            transition: 'right 0.25s ease',
          }}
        >
          <MapLegend reports={filtered} />
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
          <ViewportLabel mapCenter={mapCenter} />
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

        {/* M6: Report Detail Slide-in Panel */}
        <ReportDetailPanel
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
        />

      </div>
    </div>
  )
}

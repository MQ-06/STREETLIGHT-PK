/**
 * ClusterPopup — M9: Custom Leaflet popup for cluster bubbles
 *
 * Props:
 *   cluster     — Leaflet MarkerCluster object (for latlng + zoom)
 *   reports     — report objects extracted from cluster's child markers
 *   onQuickView — (report) => void  opens M6 slide-in panel
 *   onClose     — () => void
 *
 * Renders inside <MapContainer> using react-leaflet <Popup>.
 */
import { useRef, useEffect } from 'react'
import { Popup, useMap }     from 'react-leaflet'

// ── Helpers ───────────────────────────────────────────────────────────────────
const SEVERITY_ORDER = { large: 3, medium: 2, small: 1 }
const ICON_MAP       = { POTHOLE: '🕳️', TRASH: '🗑️' }

function sevKey(r) {
  return (r.severity || r.ai_severity || '').toLowerCase()
}

function topReports(reports) {
  return [...reports]
    .sort((a, b) => {
      const sa = SEVERITY_ORDER[sevKey(a)] ?? 0
      const sb = SEVERITY_ORDER[sevKey(b)] ?? 0
      if (sb !== sa) return sb - sa
      return new Date(b.created_at || 0) - new Date(a.created_at || 0)
    })
    .slice(0, 3)
}

function areaName(reports) {
  if (!reports.length) return 'Area'
  const counts = {}
  reports.forEach(r => {
    const city = r.assigned_city || r.location_city
    if (city) counts[city] = (counts[city] || 0) + 1
  })
  const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]
  if (!top) return 'Area'
  const name = top[0]
  return name.charAt(0).toUpperCase() + name.slice(1)
}

function cityTrend(report, allReports) {
  const now         = Date.now()
  const oneWeek     = 7  * 24 * 60 * 60 * 1000
  const twoWeeks    = 14 * 24 * 60 * 60 * 1000
  const city        = report.assigned_city
  const sameCity    = allReports.filter(r => r.assigned_city === city)

  const thisWeek = sameCity.filter(r => {
    const t = r.created_at ? new Date(r.created_at).getTime() : 0
    return t >= now - oneWeek
  }).length

  const lastWeek = sameCity.filter(r => {
    const t = r.created_at ? new Date(r.created_at).getTime() : 0
    return t >= now - twoWeeks && t < now - oneWeek
  }).length

  if (thisWeek > lastWeek) return { arrow: '↑', color: '#EF4444' }
  if (thisWeek < lastWeek) return { arrow: '↓', color: '#22C55E' }
  return { arrow: '→', color: '#64748B' }
}

const SEV_BADGE = {
  large:  { bg: '#FEE2E2', color: '#EF4444', label: 'High'   },
  medium: { bg: '#FFF7ED', color: '#F97316', label: 'Medium' },
  small:  { bg: '#F0FDF4', color: '#22C55E', label: 'Low'    },
}

// ── Sub-components ────────────────────────────────────────────────────────────
function SevBadge({ severity }) {
  const { bg, color, label } = SEV_BADGE[severity] || SEV_BADGE.medium
  return (
    <span style={{
      background: bg, color, fontSize: 10, fontWeight: 700,
      padding: '2px 7px', borderRadius: 99, whiteSpace: 'nowrap',
    }}>
      {label}
    </span>
  )
}

function ReportRow({ index, report, allReports, onQuickView }) {
  const sev   = sevKey(report)
  const trend = cityTrend(report, allReports)
  const icon  = ICON_MAP[(report.category || '').toUpperCase()] || '📋'
  const title = report.title || report.category || 'Report'
  const addr  = report.location || report.location_address || ''

  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, padding: '6px 0' }}>
      {/* Number */}
      <span style={{ fontSize: 11, fontWeight: 700, color: '#9CA3AF', minWidth: 14, paddingTop: 1 }}>
        {index}.
      </span>

      {/* Icon + title + address */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          margin: 0, fontSize: 12, fontWeight: 600, color: '#111827',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {icon} {title}
        </p>
        {addr && (
          <p style={{
            margin: '2px 0 0', fontSize: 11, color: '#9CA3AF',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>
            {addr}
          </p>
        )}
      </div>

      {/* Right side: badge + trend + quick-view */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, flexShrink: 0 }}>
        <SevBadge severity={sev} />
        <span style={{ fontSize: 12, color: trend.color, fontWeight: 700 }}>
          {trend.arrow}
        </span>
        <button
          onClick={() => onQuickView(report)}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            fontSize: 10, fontWeight: 700, color: '#E8612D',
            padding: 0, whiteSpace: 'nowrap',
          }}
        >
          Quick-view
        </button>
      </div>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ClusterPopup({ cluster, reports, onQuickView, onClose }) {
  const map      = useMap()
  const popupRef = useRef(null)

  const latlng = cluster.getLatLng()
  const count  = reports.length
  const area   = areaName(reports)
  const top3   = topReports(reports)
  const hasMore = count > 3

  // Close popup when unmounted
  useEffect(() => {
    return () => { onClose?.() }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function zoomToCluster() {
    cluster.zoomToBounds({ padding: [20, 20] })
    onClose()
  }

  return (
    <>
      {/* CSS override — injected once, scoped to .custom-cluster-popup */}
      <style>{`
        .custom-cluster-popup .leaflet-popup-content-wrapper {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 16px rgba(0,0,0,0.12);
          padding: 0;
          border: none;
        }
        .custom-cluster-popup .leaflet-popup-tip-container {
          display: none;
        }
        .custom-cluster-popup .leaflet-popup-content {
          margin: 0;
          width: 320px !important;
        }
        .custom-cluster-popup .leaflet-popup-close-button {
          display: none;
        }
      `}</style>

      <Popup
        ref={popupRef}
        position={[latlng.lat, latlng.lng]}
        className="custom-cluster-popup"
        closeButton={false}
        onClose={onClose}
        maxWidth={340}
      >
        <div style={{ padding: 16 }}>

          {/* 1. HEADER */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
            <div>
              <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: '#111827' }}>
                Cluster ({area})
              </p>
              <p style={{ margin: '2px 0 0', fontSize: 11, color: '#9CA3AF' }}>
                {count} Total Complaints
              </p>
            </div>
            <button
              onClick={onClose}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: 16, color: '#9CA3AF', lineHeight: 1, padding: 2,
              }}
              onMouseEnter={e => e.currentTarget.style.color = '#EF4444'}
              onMouseLeave={e => e.currentTarget.style.color = '#9CA3AF'}
            >
              ✕
            </button>
          </div>

          {/* 2. DIVIDER */}
          <div style={{ height: 1, background: '#F3F4F6', margin: '8px 0' }} />

          {/* 3. TOP 3 REPORTS */}
          <div>
            {top3.map((report, i) => (
              <ReportRow
                key={report.id}
                index={i + 1}
                report={report}
                allReports={reports}
                onQuickView={report => { onQuickView(report); onClose() }}
              />
            ))}
          </div>

          {/* 4. VIEW ALL FOOTER */}
          {hasMore && (
            <>
              <div style={{ height: 1, background: '#F3F4F6', margin: '8px 0' }} />
              <button
                onClick={zoomToCluster}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontSize: 11, color: '#9CA3AF', padding: 0,
                  textDecoration: 'underline',
                }}
              >
                View all {count} reports →
              </button>
            </>
          )}

        </div>
      </Popup>
    </>
  )
}

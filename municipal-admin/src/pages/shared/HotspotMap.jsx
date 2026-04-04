import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import PageHeader from '../../components/PageHeader'
import StageBadge from '../../components/StageBadge'
import { authFetch } from '../../utils/auth'

// Fix default marker icons for Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const SEV_COLOR = { high: '#EF4444', large: '#EF4444', medium: '#F97316', low: '#22C55E', small: '#22C55E' }

function coloredIcon(color) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:16px;height:16px;border-radius:50%;
      background:${color};border:2px solid #fff;
      box-shadow:0 2px 6px rgba(0,0,0,0.3);">
    </div>`,
    iconSize:   [16, 16],
    iconAnchor: [8,  8],
  })
}

function RecenterButton({ center }) {
  const map = useMap()
  return (
    <button
      onClick={() => map.setView(center, 12)}
      className="absolute bottom-8 right-4 z-50 bg-white shadow-md px-3 py-2 rounded-xl text-xs font-bold text-gray-700 border border-warm-border"
    >
      Re-center
    </button>
  )
}

const STAGE_OPTIONS = ['', 'NEW', 'PENDING_VERIFICATION', 'VERIFIED', 'IN_PROGRESS', 'AWAITING_FEEDBACK', 'RESOLVED']
const SEV_OPTIONS   = ['', 'high', 'medium', 'low']

// Default center: Lahore
const DEFAULT_CENTER = [31.5204, 74.3587]

export default function HotspotMap() {
  const navigate = useNavigate()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [stage,   setStage]   = useState('')
  const [sev,     setSev]     = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ limit: 200 })
      if (stage) params.set('stage', stage)
      const res  = await authFetch('/admin/reports?' + params)
      const data = await res.json()
      setReports((data.reports || []).filter(r => r.lat && r.lng))
    } catch {
      setReports([])
    } finally {
      setLoading(false)
    }
  }, [stage])

  useEffect(() => { load() }, [load])

  const filtered = sev
    ? reports.filter(r => (r.severity || '').toLowerCase() === sev)
    : reports

  return (
    <div className="p-6 flex flex-col gap-5">
      <PageHeader
        title="Hotspot Map"
        subtitle={filtered.length + ' complaint' + (filtered.length !== 1 ? 's' : '') + ' with location data'}
      />

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <select
          value={stage} onChange={e => setStage(e.target.value)}
          className="bg-white border border-warm-border rounded-xl px-3 py-2 text-sm text-gray-700 outline-none"
        >
          <option value="">All Stages</option>
          {STAGE_OPTIONS.filter(Boolean).map(s => (
            <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
          ))}
        </select>
        <select
          value={sev} onChange={e => setSev(e.target.value)}
          className="bg-white border border-warm-border rounded-xl px-3 py-2 text-sm text-gray-700 outline-none"
        >
          <option value="">All Severities</option>
          {SEV_OPTIONS.filter(Boolean).map(s => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
        <div className="flex items-center gap-3 ml-auto text-xs text-gray-500">
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: '#EF4444' }} /> High</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: '#F97316' }} /> Medium</span>
          <span className="flex items-center gap-1"><span className="w-3 h-3 rounded-full inline-block" style={{ background: '#22C55E' }} /> Low</span>
        </div>
      </div>

      {/* Map */}
      <div className="relative rounded-3xl overflow-hidden border border-warm-border shadow-sm" style={{ height: 520 }}>
        {loading && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-white/70">
            <span className="text-sm text-gray-500">Loading map data…</span>
          </div>
        )}
        <MapContainer center={DEFAULT_CENTER} zoom={12} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filtered.map(r => {
            const color = SEV_COLOR[(r.severity || 'medium').toLowerCase()] || '#F97316'
            return (
              <Marker key={r.id} position={[r.lat, r.lng]} icon={coloredIcon(color)}>
                <Popup minWidth={220}>
                  <div className="text-sm">
                    <p className="font-bold text-gray-800 mb-1">{r.display_id} — {r.title}</p>
                    {r.location && <p className="text-gray-500 text-xs mb-1">📍 {r.location}</p>}
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className="text-xs font-bold px-2 py-0.5 rounded-full"
                        style={{ backgroundColor: color + '20', color }}
                      >
                        {r.severity}
                      </span>
                      <span className="text-xs text-gray-500">{r.kanban_stage?.replace(/_/g, ' ')}</span>
                    </div>
                    <button
                      onClick={() => navigate('/complaint-detail/' + r.id)}
                      className="text-xs font-bold underline"
                      style={{ color: '#B85C2E' }}
                    >
                      View Detail →
                    </button>
                  </div>
                </Popup>
              </Marker>
            )
          })}
          <RecenterButton center={DEFAULT_CENTER} />
        </MapContainer>
      </div>

      {filtered.length === 0 && !loading && (
        <p className="text-center text-sm text-gray-400 py-4">
          No complaints with GPS coordinates found for the current filters.
        </p>
      )}
    </div>
  )
}

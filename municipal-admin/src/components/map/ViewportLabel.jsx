/**
 * ViewportLabel — M5b: Bottom-center floating area name pill
 *
 * Props:
 *   mapCenter — Leaflet LatLng object (updated on pan/zoom)
 *
 * Reverse-geocodes the center via Nominatim (max 1 req / 2 s).
 * Displays "Current View: {suburb or city_district or city}"
 */
import { useState, useEffect, useRef } from 'react'

const C = {
  bg:     '#111A2E',
  border: '#1C2A45',
  muted:  '#64748B',
}

const THROTTLE_MS = 2000   // Nominatim usage policy: max 1 req/s, we use 2 s

async function reverseGeocode(lat, lng) {
  const url = `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`
  const res  = await fetch(url, { headers: { 'Accept-Language': 'en' } })
  const data = await res.json()
  const addr = data.address || {}
  return (
    addr.suburb        ||
    addr.city_district ||
    addr.town          ||
    addr.city          ||
    addr.county        ||
    'Unknown Area'
  )
}

export default function ViewportLabel({ mapCenter }) {
  const [areaName,  setAreaName]  = useState('Loading…')
  const lastFetchAt = useRef(0)
  const timerRef    = useRef(null)

  useEffect(() => {
    if (!mapCenter) return

    const lat = mapCenter.lat
    const lng = mapCenter.lng

    // Cancel any pending throttled call
    if (timerRef.current) clearTimeout(timerRef.current)

    const now   = Date.now()
    const delay = Math.max(0, THROTTLE_MS - (now - lastFetchAt.current))

    timerRef.current = setTimeout(async () => {
      lastFetchAt.current = Date.now()
      try {
        const name = await reverseGeocode(lat, lng)
        setAreaName(name)
      } catch {
        setAreaName('Unknown Area')
      }
    }, delay)

    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  }, [mapCenter])

  return (
    <div style={{
      background:   C.bg,
      border:       `1px solid ${C.border}`,
      borderRadius: 20,
      padding:      '6px 16px',
    }}>
      <span style={{ fontSize: 11, color: C.muted }}>
        Current View: <strong style={{ color: C.muted }}>{areaName}</strong>
      </span>
    </div>
  )
}

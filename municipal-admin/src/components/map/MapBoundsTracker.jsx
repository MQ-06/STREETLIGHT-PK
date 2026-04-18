/**
 * MapBoundsTracker — lives inside <MapContainer> to access useMap().
 * Calls onBoundsChange(bounds) and onCenterChange(center) on mount
 * and every 'moveend' event.
 *
 * Props:
 *   onBoundsChange — (LatLngBounds) => void
 *   onCenterChange — (LatLng) => void  (optional)
 */
import { useEffect } from 'react'
import { useMap } from 'react-leaflet'

export default function MapBoundsTracker({ onBoundsChange, onCenterChange }) {
  const map = useMap()

  useEffect(() => {
    const fire = () => {
      onBoundsChange(map.getBounds())
      onCenterChange?.(map.getCenter())
    }

    fire()   // fire immediately with initial values
    map.on('moveend', fire)
    return () => { map.off('moveend', fire) }
  }, [map, onBoundsChange, onCenterChange])

  return null
}

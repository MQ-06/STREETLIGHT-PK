/**
 * MapBoundsTracker — lives inside <MapContainer> to access useMap().
 * Calls onBoundsChange(bounds) on mount and every 'moveend' event.
 *
 * Props:
 *   onBoundsChange — (LatLngBounds) => void
 */
import { useEffect } from 'react'
import { useMap } from 'react-leaflet'

export default function MapBoundsTracker({ onBoundsChange }) {
  const map = useMap()

  useEffect(() => {
    // Fire immediately with the initial bounds
    onBoundsChange(map.getBounds())

    const handler = () => onBoundsChange(map.getBounds())
    map.on('moveend', handler)
    return () => { map.off('moveend', handler) }
  }, [map, onBoundsChange])

  return null
}

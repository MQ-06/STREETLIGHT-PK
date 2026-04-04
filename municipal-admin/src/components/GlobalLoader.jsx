import { useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'

/**
 * A sleek top-bar loading indicator that triggers on every route transition.
 * Simulates a fast network request progress bar (like GitHub or Next.js)
 */
export default function GlobalLoader() {
  const location = useLocation()
  const [progress, setProgress] = useState(0)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    setVisible(true)
    setProgress(15) // Jump to 15% immediately
    
    // Increment gradually
    const interval = setInterval(() => {
      setProgress(p => Math.min(p + 15, 85))
    }, 100)

    // Complete loader
    const completeTimeout = setTimeout(() => {
      setProgress(100)
      setTimeout(() => setVisible(false), 400) // Wait for fade out
      clearInterval(interval)
    }, 400)

    return () => {
      clearInterval(interval)
      clearTimeout(completeTimeout)
    }
  }, [location.pathname])

  if (!visible) return null

  return (
    <div className="fixed top-0 left-0 w-full h-[3px] z-[9999] pointer-events-none overflow-hidden">
      <div 
        className="h-full bg-[#B85C2E] rounded-r-full"
        style={{ 
          width: `${progress}%`, 
          opacity: progress === 100 ? 0 : 1,
          boxShadow: '0 0 15px rgba(184, 92, 46, 0.8)',
          transition: 'width 250ms ease-out, opacity 300ms ease-in-out'
        }}
      />
    </div>
  )
}

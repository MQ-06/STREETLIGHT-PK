// M5 placeholder — Viewport Label (bottom-center floating)
export default function ViewportLabel({ count }) {
  return (
    <div style={{
      background: '#111A2E', border: '1px solid #1C2A45',
      borderRadius: 20, padding: '6px 16px',
      color: '#64748B', fontSize: 12,
    }}>
      M5 — {count} reports in view
    </div>
  )
}

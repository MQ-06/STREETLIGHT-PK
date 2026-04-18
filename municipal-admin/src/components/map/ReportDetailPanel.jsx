// M6 placeholder — Report Detail Slide-in Panel
export default function ReportDetailPanel({ report, onClose }) {
  if (!report) return null
  return (
    <div style={{
      position: 'absolute', top: 0, right: 0, bottom: 0, width: 360,
      background: '#111A2E', borderLeft: '1px solid #1C2A45',
      zIndex: 1000, padding: 24, color: '#E2E8F0', fontSize: 13,
    }}>
      <button onClick={onClose} style={{ color: '#64748B', background: 'none', border: 'none', cursor: 'pointer', marginBottom: 16 }}>
        ✕ Close
      </button>
      <p>M6 — Report Detail Panel</p>
      <p style={{ color: '#64748B', marginTop: 8 }}>ID: {report.id}</p>
    </div>
  )
}

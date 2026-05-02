import { useState } from 'react'
import { Download } from 'lucide-react'
import { downloadDashboardAnalyticsCsv } from '../../utils/exportDashboardAnalyticsCsv'

export default function ExportAnalyticsCsvButton({ days }) {
  const [busy, setBusy] = useState(false)

  return (
    <button
      type="button"
      disabled={busy}
      onClick={async () => {
        setBusy(true)
        try {
          await downloadDashboardAnalyticsCsv(days)
        } catch {
          window.alert('Could not export CSV. Check your session and try again.')
        } finally {
          setBusy(false)
        }
      }}
      className="flex items-center gap-2 px-4 py-2 rounded-xl border border-warm-border bg-white text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-colors"
    >
      <Download size={14} /> {busy ? 'Exporting…' : 'Export CSV'}
    </button>
  )
}

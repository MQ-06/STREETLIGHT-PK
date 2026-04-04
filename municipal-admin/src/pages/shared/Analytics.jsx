import { useNavigate } from 'react-router-dom'
import { Calendar, Download, MapPin, TrendingUp, TrendingDown } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { useDashboard } from '../../hooks/useDashboard'

const BREAKDOWN = [
  { label: 'Streetlights',     pct: 35, color: '#B85C2E' },
  { label: 'Waste Management', pct: 25, color: '#EAB308' },
  { label: 'Road & Potholes',  pct: 20, color: '#22C55E' },
  { label: 'Water Supply',     pct: 20, color: '#3B82F6' },
]
const DEPARTMENTS = [
  { name: 'LMC',  hrs: 12.4, pct: 50 },
  { name: 'LWMC', hrs: 18.2, pct: 68 },
  { name: 'FMC',  hrs: 24.5, pct: 90 },
  { name: 'FWMC', hrs: 9.1,  pct: 38 },
]
const PROBLEM_AREAS = [
  { location: '5th Avenue, Downtown', issue: 'Broken Streetlights', freq: '12/mo', trend: '+15%', up: true,  statusBg: '#FFF7ED', statusColor: '#F97316', status: 'High Alert' },
  { location: 'Park Lane Crossing',   issue: 'Illegal Dumping',     freq: '8/mo',  trend: '-4%',  up: false, statusBg: '#F3F4F6', statusColor: '#6B7280', status: 'Monitoring' },
  { location: 'Industrial Zone East', issue: 'Water Leakage',       freq: '21/mo', trend: '+32%', up: true,  statusBg: '#FEF2F2', statusColor: '#EF4444', status: 'Critical'   },
]

function DonutChart() {
  const segs = [{ pct:35,color:'#B85C2E'},{pct:25,color:'#EAB308'},{pct:20,color:'#22C55E'},{pct:20,color:'#3B82F6'}]
  const r = 68, circ = 2 * Math.PI * r, gap = 3
  let off = 0
  const slices = segs.map(s => { const dash = (s.pct/100)*circ - gap; const sl = {...s, dash, off}; off += (s.pct/100)*circ; return sl })
  return (
    <svg width="176" height="176" viewBox="0 0 176 176">
      {slices.map((s,i) => (
        <circle key={i} cx="88" cy="88" r={r} fill="none" stroke={s.color} strokeWidth="20"
          strokeDasharray={s.dash + ' ' + (circ - s.dash)} strokeDashoffset={-s.off + circ * 0.25} />
      ))}
      <text x="88" y="82"  textAnchor="middle" fontSize="24" fontWeight="800" fill="#111827">100%</text>
      <text x="88" y="100" textAnchor="middle" fontSize="8"  fontWeight="600" fill="#9CA3AF" letterSpacing="1.5">TOTAL VOLUME</text>
    </svg>
  )
}

export default function Analytics() {
  const navigate = useNavigate()
  const { data, loading } = useDashboard()
  const kc = data?.kanban_counts || {}
  const total = data?.total ?? 0
  const resolved = kc.RESOLVED || 0
  const resRate = total ? ((resolved / total) * 100).toFixed(1) : '—'

  const STATS = [
    { icon: '📋', iconBg: '#FFF7ED', change: '+12.4%', changeColor: '#22C55E', label: 'Total Reports',        value: loading ? '…' : String(total)         },
    { icon: '✅', iconBg: '#F0FDF4', change: '+8.1%',  changeColor: '#22C55E', label: 'Resolution Rate',      value: loading ? '…' : resRate + '%'         },
    { icon: '⏱', iconBg: '#EFF6FF', change: '-2.4h',  changeColor: '#EF4444', label: 'Avg. Resolution Time', value: '18.5 hrs'                             },
    { icon: '⭐', iconBg: '#FEFCE8', change: '+0.4',   changeColor: '#22C55E', label: 'Citizen Satisfaction', value: '4.8 / 5.0'                           },
  ]

  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Analytics & Performance" subtitle="Real-time insights into municipal efficiency and public engagement.">
        <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white shadow-sm text-sm font-medium text-gray-600 border border-warm-border">
          <Calendar size={14} /> Last 30 Days
        </button>
        <button className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-sm font-semibold bg-primary hover:bg-primary-dark">
          <Download size={14} /> Export Report
        </button>
      </PageHeader>

      <div className="grid grid-cols-4 gap-4">
        {STATS.map(s => (
          <div key={s.label} className="bg-white rounded-3xl p-5 shadow-sm border border-warm-border flex flex-col gap-3 cursor-pointer hover:shadow-md" onClick={() => navigate('/complaint-management')}>
            <div className="flex items-center justify-between">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg" style={{ backgroundColor: s.iconBg }}>{s.icon}</div>
              <span className="text-xs font-bold" style={{ color: s.changeColor }}>{s.change}</span>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">{s.label}</p>
              <p className="text-2xl font-black text-gray-900">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-5">
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border shrink-0" style={{ width: 300 }}>
          <h2 className="text-base font-bold text-gray-900 mb-5">Complaint Breakdown</h2>
          <div className="flex justify-center mb-5"><DonutChart /></div>
          <div className="flex flex-col gap-3">
            {BREAKDOWN.map(b => (
              <div key={b.label} className="flex items-center justify-between cursor-pointer hover:opacity-70" onClick={() => navigate('/complaint-management')}>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: b.color }} />
                  <span className="text-sm text-gray-600">{b.label}</span>
                </div>
                <span className="text-sm font-bold text-gray-700">{b.pct}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-base font-bold text-gray-900">Dept. Resolution Times (Hrs)</h2>
          </div>
          <div className="flex flex-col gap-5">
            {DEPARTMENTS.map(d => (
              <div key={d.name} className="cursor-pointer hover:opacity-70" onClick={() => navigate('/departments')}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-700">{d.name}</span>
                  <span className="text-sm font-bold text-gray-800">{d.hrs}h</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                  <div className="h-full rounded-full bg-primary" style={{ width: d.pct + '%' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-3xl p-6 shadow-sm border border-warm-border">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-lg font-black text-gray-900">Recurring Problem Areas</h2>
          <button onClick={() => navigate('/hotspot-map')} className="text-sm font-bold text-primary">View Map</button>
        </div>
        <table className="w-full mt-4">
          <thead>
            <tr className="text-left border-b border-gray-50">
              {['Location', 'Primary Issue', 'Frequency', 'Trend', 'Status'].map(h => (
                <th key={h} className="text-xs font-medium text-gray-400 pb-3 pr-6">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PROBLEM_AREAS.map((row, i) => (
              <tr key={i} className="border-b last:border-0 cursor-pointer hover:bg-gray-50" onClick={() => navigate('/complaint-management')}>
                <td className="py-4 pr-6">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center"><MapPin size={12} className="text-gray-400" /></div>
                    <span className="text-sm text-gray-800">{row.location}</span>
                  </div>
                </td>
                <td className="py-4 pr-6 text-sm text-gray-600">{row.issue}</td>
                <td className="py-4 pr-6 text-sm text-gray-600">{row.freq}</td>
                <td className="py-4 pr-6">
                  <div className="flex items-center gap-1 text-sm font-bold" style={{ color: row.up ? '#EF4444' : '#22C55E' }}>
                    {row.up ? <TrendingUp size={13} /> : <TrendingDown size={13} />} {row.trend}
                  </div>
                </td>
                <td className="py-4">
                  <span className="text-xs font-bold px-3 py-1 rounded-full" style={{ backgroundColor: row.statusBg, color: row.statusColor }}>{row.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

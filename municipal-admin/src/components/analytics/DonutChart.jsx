// Module 2 — Issue type donut chart (Recharts)
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = ['#B85C2E', '#F59E0B', '#3B82F6', '#22C55E', '#8B5CF6', '#EC4899']

const LABEL_MAP = {
  POTHOLE: 'Pothole',
  TRASH:   'Trash',
  UNKNOWN: 'Unknown',
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-white border border-warm-border rounded-xl px-3 py-2 shadow text-xs">
      <p className="font-bold text-gray-800">{d.name}</p>
      <p className="text-gray-500">{d.value} reports · {d.pct}%</p>
    </div>
  )
}

export default function DonutChart({ data, title }) {
  if (!data?.length) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-300">
        No data for this period
      </div>
    )
  }

  const slices = data.map((d, i) => ({
    name:  LABEL_MAP[d.category] ?? d.category,
    value: d.count,
    pct:   d.pct,
    fill:  COLORS[i % COLORS.length],
  }))

  return (
    <div>
      <p className="text-sm font-semibold text-gray-700 mb-1">{title}</p>
      {/* Explicit height wrapper is required — ResponsiveContainer collapses inside CSS grid without it */}
      <div style={{ width: '100%', height: 220 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={slices}
            dataKey="value"
            innerRadius="52%"
            outerRadius="78%"
            paddingAngle={3}
            stroke="none"
          >
            {slices.map((s, i) => <Cell key={i} fill={s.fill} />)}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={v => <span className="text-xs text-gray-600">{v}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
      </div>
    </div>
  )
}

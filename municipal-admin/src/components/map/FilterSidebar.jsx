/**
 * FilterSidebar — M2: Left Sidebar Filter Panel
 *
 * Props:
 *   filters        — current filter state from useMapReports
 *   setFilter      — (key, value) => void
 *   recentReports  — the filtered array (we show top-5 by recency)
 *   onReportClick  — (report) => void  fly + open detail panel
 */
import { useState } from 'react'
import { useAdminSearch } from '../../context/AdminSearchContext'

// ── Design tokens ─────────────────────────────────────────────────────────────
const C = {
  bg:       '#111A2E',
  surface:  '#162037',
  border:   '#1C2A45',
  text:     '#E2E8F0',
  muted:    '#64748B',
  orange:   '#E8612D',
  orangeBg: 'rgba(232,97,45,0.15)',
}

// ── Severity accent colours ────────────────────────────────────────────────
const SEVERITY_COLOR = {
  large:  '#EF4444',
  medium: '#F97316',
  small:  '#22C55E',
}

// ── Filter option definitions ──────────────────────────────────────────────
const CATEGORY_OPTIONS = [
  { label: 'All',     value: '' },
  { label: 'Pothole', value: 'POTHOLE' },
  { label: 'Trash',   value: 'TRASH' },
]

const STAGE_OPTIONS = [
  { label: 'All',         value: '' },
  { label: 'New',         value: 'NEW' },
  { label: 'Pending',     value: 'PENDING_VERIFICATION' },
  { label: 'In Progress', value: 'IN_PROGRESS' },
  { label: 'Resolved',    value: 'RESOLVED' },
]

const TIME_OPTIONS = [
  { label: 'Last 24 Hours', value: '24h' },
  { label: 'Last 7 Days',   value: '7d' },
  { label: 'Last 30 Days',  value: '30d' },
]

const SEVERITY_OPTIONS = [
  { label: 'Low',    value: 'small' },
  { label: 'Medium', value: 'medium' },
  { label: 'High',   value: 'large' },
]

// ── Helpers ───────────────────────────────────────────────────────────────────
function timeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins  = Math.floor(diff / 60000)
  if (mins < 60)   return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs  < 24)   return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function top5Recent(reports) {
  return [...reports]
    .filter(r => r.created_at)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5)
}

// ── Sub-components ────────────────────────────────────────────────────────────

function SectionLabel({ children }) {
  return (
    <p style={{
      margin: '0 0 8px',
      fontSize: 10,
      fontWeight: 700,
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      color: C.muted,
    }}>
      {children}
    </p>
  )
}

function Divider() {
  return <div style={{ height: 1, background: C.border, margin: '16px 0' }} />
}

/** Dark styled <select> for Issue Type */
function DarkSelect({ value, onChange, options }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      style={{
        width:              '100%',
        background:         C.surface,
        border:             `1px solid ${value ? C.orange : C.border}`,
        borderRadius:       6,
        color:              C.text,
        fontSize:           13,
        padding:            '7px 30px 7px 10px',
        cursor:             'pointer',
        outline:            'none',
        appearance:         'none',
        WebkitAppearance:   'none',
        backgroundImage:    `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2364748B' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E")`,
        backgroundRepeat:   'no-repeat',
        backgroundPosition: 'right 10px center',
      }}
    >
      {options.map(o => (
        <option key={o.value} value={o.value} style={{ background: C.surface }}>
          {o.label}
        </option>
      ))}
    </select>
  )
}

/** Radio-dot row used for Status + Severity */
function RadioGroup({ options, value, onChange }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {options.map(opt => {
        const active = value === opt.value
        return (
          <button
            key={opt.value}
            onClick={() => onChange(active ? '' : opt.value)}
            style={{
              display:    'flex',
              alignItems: 'center',
              gap:        10,
              background: 'none',
              border:     'none',
              cursor:     'pointer',
              padding:    '4px 0',
              textAlign:  'left',
            }}
          >
            <span style={{
              width:        14,
              height:       14,
              borderRadius: '50%',
              border:       `2px solid ${active ? C.orange : C.muted}`,
              background:   active ? C.orange : 'transparent',
              flexShrink:   0,
              display:      'inline-block',
            }} />
            <span style={{ fontSize: 13, color: active ? C.text : C.muted }}>
              {opt.label}
            </span>
          </button>
        )
      })}
    </div>
  )
}

/** Pill-style radio for Time Range */
function TimeRangeGroup({ value, onChange }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {TIME_OPTIONS.map(opt => {
        const active = value === opt.value
        return (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            style={{
              background:   active ? C.orangeBg : 'transparent',
              border:       `1px solid ${active ? C.orange : 'transparent'}`,
              borderRadius: 6,
              color:        active ? C.orange : C.muted,
              fontSize:     13,
              fontWeight:   active ? 600 : 400,
              padding:      '6px 10px',
              cursor:       'pointer',
              textAlign:    'left',
            }}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}

/** Single recent report card */
function RecentCard({ report, onClick }) {
  const color    = SEVERITY_COLOR[report.ai_severity] || C.muted
  const category = report.category || 'Report'
  const title    = category.charAt(0) + category.slice(1).toLowerCase()
  const reporter = report.reporter_name || report.reporter_username || 'Unknown'

  return (
    <button
      onClick={() => onClick(report)}
      style={{
        display:      'block',
        width:        '100%',
        background:   C.surface,
        border:       `1px solid ${C.border}`,
        borderLeft:   `3px solid ${color}`,
        borderRadius: 6,
        padding:      '8px 10px',
        marginBottom: 6,
        cursor:       'pointer',
        textAlign:    'left',
      }}
    >
      <p style={{
        margin:       0,
        fontSize:     13,
        fontWeight:   600,
        color:        C.text,
        whiteSpace:   'nowrap',
        overflow:     'hidden',
        textOverflow: 'ellipsis',
      }}>
        {title}
      </p>
      <p style={{ margin: '3px 0 0', fontSize: 11, color: C.muted }}>
        {reporter} · {timeAgo(report.created_at)}
      </p>
    </button>
  )
}

// ── Main component ────────────────────────────────────────────────────────────
export default function FilterSidebar({ filters, setFilter, recentReports = [], onReportClick }) {
  const [collapsed, setCollapsed] = useState(false)
  const { query: globalSearch } = useAdminSearch()

  const recent = top5Recent(recentReports)

  return (
    <div style={{
      width:         '100%',
      height:        '100%',
      display:       'flex',
      flexDirection: 'column',
      overflowY:     'auto',
    }}>

      {/* ── Collapse toggle header ── */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        '14px 16px',
        borderBottom:   `1px solid ${C.border}`,
        flexShrink:     0,
      }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: C.text }}>
          Filters
        </span>
        <button
          onClick={() => setCollapsed(c => !c)}
          style={{
            background: 'none',
            border:     'none',
            cursor:     'pointer',
            color:      C.muted,
            fontSize:   18,
            lineHeight: 1,
            padding:    0,
            transform:  collapsed ? 'rotate(-90deg)' : 'rotate(90deg)',
            transition: 'transform 0.2s ease',
          }}
          aria-label={collapsed ? 'Expand filters' : 'Collapse filters'}
        >
          ›
        </button>
      </div>

      {/* ── Collapsible body ── */}
      {!collapsed && (
        <div style={{ padding: '16px', flex: 1, overflowY: 'auto' }}>

          {globalSearch.trim() ? (
            <p style={{ margin: '0 0 14px', fontSize: 11, color: C.orange, lineHeight: 1.45 }}>
              Global search: &quot;{globalSearch.trim()}&quot; — pins respect this plus filters below.
            </p>
          ) : null}

          {/* Issue Type */}
          <SectionLabel>Issue Type</SectionLabel>
          <DarkSelect
            value={filters.category}
            onChange={v => setFilter('category', v)}
            options={CATEGORY_OPTIONS}
          />

          <Divider />

          {/* Status */}
          <SectionLabel>Status</SectionLabel>
          <RadioGroup
            options={STAGE_OPTIONS}
            value={filters.stage}
            onChange={v => setFilter('stage', v)}
          />

          <Divider />

          {/* Time Range */}
          <SectionLabel>Time Range</SectionLabel>
          <TimeRangeGroup
            value={filters.timeRange}
            onChange={v => setFilter('timeRange', v)}
          />

          <Divider />

          {/* Severity */}
          <SectionLabel>Severity</SectionLabel>
          <RadioGroup
            options={SEVERITY_OPTIONS}
            value={filters.severity}
            onChange={v => setFilter('severity', v)}
          />

          <Divider />

          {/* Recent Reports */}
          <SectionLabel>Recent Reports</SectionLabel>
          {recent.length === 0 ? (
            <p style={{ fontSize: 12, color: C.muted, margin: 0 }}>
              No reports match current filters.
            </p>
          ) : (
            recent.map(r => (
              <RecentCard
                key={r.id}
                report={r}
                onClick={onReportClick}
              />
            ))
          )}

        </div>
      )}
    </div>
  )
}

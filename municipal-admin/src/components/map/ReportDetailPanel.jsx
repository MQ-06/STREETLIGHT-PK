/**
 * ReportDetailPanel — M6: Read-only report slide-in panel
 *
 * Props:
 *   report  — list-API report object (basic fields); null when closed
 *   onClose — () => void
 *
 * On open: fetches GET /admin/reports/{id} for full details
 * (trust_score, community_score, reporter_impact_score, etc.)
 */
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { authFetch } from '../../utils/auth'
import { getBadge }  from '../../utils/badge'

// ── Stepper helpers ───────────────────────────────────────────────────────────
const STEPS = ['Pending', 'In Progress', 'Resolved']

function stageToStep(stage) {
  const s = (stage || '').toUpperCase()
  if (s === 'RESOLVED' || s === 'CLOSED') return 3
  if (s === 'IN_PROGRESS' || s === 'AWAITING_FEEDBACK') return 2
  return 1
}

// ── Severity badge ────────────────────────────────────────────────────────────
function SeverityBadge({ severity }) {
  const s = (severity || '').toLowerCase()
  const map = {
    large:  { bg: '#FEE2E2', color: '#EF4444', label: '⚠ HIGH' },
    medium: { bg: '#FFF7ED', color: '#F97316', label: 'MEDIUM' },
    small:  { bg: '#F0FDF4', color: '#22C55E', label: 'LOW' },
  }
  const { bg, color, label } = map[s] || map.medium
  return (
    <span style={{
      background: bg, color, fontSize: 11, fontWeight: 700,
      padding: '3px 10px', borderRadius: 20,
    }}>
      {label}
    </span>
  )
}

// ── Skeleton shimmer ──────────────────────────────────────────────────────────
function Skeleton({ h = 16, w = '100%', r = 6 }) {
  return (
    <div style={{
      height: h, width: w, borderRadius: r,
      background: 'linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.4s infinite',
    }} />
  )
}

// ── Divider ───────────────────────────────────────────────────────────────────
function SectionCard({ children }) {
  return (
    <div style={{
      border: '1px solid #F3F4F6', borderRadius: 12, padding: '12px 14px',
    }}>
      {children}
    </div>
  )
}

function Label({ children }) {
  return (
    <p style={{ margin: '0 0 4px', fontSize: 11, color: '#9CA3AF', fontWeight: 500 }}>
      {children}
    </p>
  )
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ReportDetailPanel({ report, onClose }) {
  const navigate    = useNavigate()
  const [detail, setDetail]   = useState(null)
  const [loading, setLoading] = useState(false)
  const panelRef = useRef(null)

  // Fetch full details when report changes
  useEffect(() => {
    if (!report) { setDetail(null); return }
    setLoading(true)
    setDetail(null)
    authFetch(`/admin/reports/${report.id}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => setDetail(d))
      .catch(() => setDetail(null))
      .finally(() => setLoading(false))
  }, [report?.id])

  // Click-outside to close
  useEffect(() => {
    if (!report) return
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) onClose()
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [report, onClose])

  const isOpen = Boolean(report)
  const data   = detail || report || {}

  const score        = data.ai_confidence ?? 0
  const activeStep   = stageToStep(data.kanban_stage)
  const badge        = detail ? getBadge(detail.reporter_impact_score) : null
  const category     = (data.category || '').toLowerCase()
  const categoryIcon = category === 'pothole' ? '🛣️' : category === 'trash' ? '🗑️' : '📋'
  const categoryLabel = category.charAt(0).toUpperCase() + category.slice(1)

  return (
    <>
      {/* shimmer keyframes */}
      <style>{`
        @keyframes shimmer {
          0%   { background-position: 200% 0 }
          100% { background-position: -200% 0 }
        }
      `}</style>

      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position:   'absolute', inset: 0,
          background: 'rgba(0,0,0,0.30)',
          zIndex:     1050,
          opacity:    isOpen ? 1 : 0,
          pointerEvents: isOpen ? 'auto' : 'none',
          transition: 'opacity 0.3s ease',
        }}
      />

      {/* Slide-in panel */}
      <div
        ref={panelRef}
        style={{
          position:   'absolute', top: 0, right: 0, bottom: 0,
          width:      380,
          background: '#FFFFFF',
          borderLeft: '1px solid #E5E7EB',
          borderRadius: '16px 0 0 16px',
          boxShadow:  '0 4px 24px rgba(0,0,0,0.15)',
          zIndex:     1100,
          transform:  isOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease-out',
          display:    'flex',
          flexDirection: 'column',
          overflowY:  'auto',
          padding:    '20px',
          gap:        14,
        }}
      >
        {!report ? null : (
          <>
            {/* 1. HEADER */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 16, fontWeight: 700, color: '#111827' }}>
                Report Details
              </span>
              <button
                onClick={onClose}
                style={{
                  background: 'none', border: 'none', cursor: 'pointer',
                  fontSize: 18, color: '#9CA3AF', lineHeight: 1, padding: 4,
                  borderRadius: 6,
                }}
                onMouseEnter={e => e.target.style.color = '#EF4444'}
                onMouseLeave={e => e.target.style.color = '#9CA3AF'}
              >
                ✕
              </button>
            </div>

            {/* 2. PHOTO */}
            <div>
              {data.image_url ? (
                <img
                  src={data.image_url}
                  alt="report"
                  style={{
                    width: '100%', height: 200, objectFit: 'cover',
                    borderRadius: 12, display: 'block',
                  }}
                />
              ) : (
                <div style={{
                  width: '100%', height: 200, borderRadius: 12,
                  background: '#F3F4F6', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                  flexDirection: 'column', gap: 6,
                }}>
                  <span style={{ fontSize: 32 }}>📷</span>
                  <span style={{ fontSize: 11, color: '#9CA3AF' }}>No photo available</span>
                </div>
              )}
              <p style={{ margin: '6px 0 0', fontSize: 11, color: '#9CA3AF' }}>
                Reported {categoryLabel}
              </p>
            </div>

            {loading ? (
              /* Skeleton while fetching detail */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <Skeleton h={40} r={12} />
                <Skeleton h={60} r={12} />
                <Skeleton h={60} r={12} />
                <Skeleton h={80} r={12} />
              </div>
            ) : (
              <>
                {/* 3. ID + TYPE */}
                <SectionCard>
                  <div style={{ display: 'flex', gap: 0 }}>
                    <div style={{ flex: 1 }}>
                      <Label>Report ID</Label>
                      <p style={{ margin: 0, fontSize: 18, fontWeight: 800, color: '#111827' }}>
                        {data.display_id || `#SR-${String(data.id).padStart(4,'0')}`}
                      </p>
                    </div>
                    <div style={{ width: 1, background: '#F3F4F6', margin: '0 12px' }} />
                    <div style={{ flex: 1 }}>
                      <Label>Issue Type</Label>
                      <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: '#111827' }}>
                        {categoryIcon} {categoryLabel}
                      </p>
                    </div>
                  </div>
                </SectionCard>

                {/* 4. SEVERITY + AI SCORE */}
                <SectionCard>
                  <div style={{ display: 'flex', gap: 0 }}>
                    <div style={{ flex: 1 }}>
                      <Label>Severity</Label>
                      <SeverityBadge severity={data.severity} />
                    </div>
                    <div style={{ width: 1, background: '#F3F4F6', margin: '0 12px' }} />
                    <div style={{ flex: 1 }}>
                      <Label>AI Confidence Score</Label>
                      <p style={{ margin: '0 0 6px', fontSize: 20, fontWeight: 800, color: '#111827' }}>
                        {score}/100
                      </p>
                      <div style={{ height: 6, borderRadius: 99, background: '#F3F4F6', overflow: 'hidden' }}>
                        <div style={{
                          height: '100%', width: `${score}%`,
                          background: '#E8612D', borderRadius: 99,
                          transition: 'width 0.4s ease',
                        }} />
                      </div>
                    </div>
                  </div>
                </SectionCard>

                {/* 5. REPORTER TRUST */}
                <SectionCard>
                  <Label>Reporter Trust</Label>
                  {badge && badge.tierLevel > 0 ? (
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 5,
                      background: badge.bg, color: badge.color,
                      fontSize: 12, fontWeight: 700,
                      padding: '4px 12px', borderRadius: 20,
                    }}>
                      {badge.icon} {badge.subBadge}
                      <span style={{ opacity: 0.6, fontWeight: 400, marginLeft: 4 }}>
                        · {badge.tier}
                      </span>
                    </span>
                  ) : (
                    <span style={{ fontSize: 12, color: '#9CA3AF' }}>
                      Trust data unavailable
                    </span>
                  )}
                  {detail?.reporter_name && (
                    <p style={{ margin: '6px 0 0', fontSize: 11, color: '#9CA3AF' }}>
                      {detail.reporter_name}
                    </p>
                  )}
                </SectionCard>

                {/* 6. STATUS TIMELINE */}
                <SectionCard>
                  <Label>Status Timeline</Label>

                  {/* Stepper */}
                  <div style={{ display: 'flex', alignItems: 'center', margin: '10px 0 8px' }}>
                    {STEPS.map((step, i) => {
                      const pos  = i + 1
                      const past = activeStep > pos
                      const active = activeStep === pos
                      const dotColor = active ? '#E8612D' : past ? '#9CA3AF' : 'transparent'
                      const dotBorder = active || past ? 'none' : '2px solid #D1D5DB'
                      return (
                        <div key={step} style={{ display: 'flex', alignItems: 'center', flex: i < 2 ? 1 : 0 }}>
                          {/* Dot */}
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                            <div style={{
                              width: 14, height: 14, borderRadius: '50%',
                              background: dotColor,
                              border: dotBorder,
                              boxShadow: active ? '0 0 0 4px rgba(232,97,45,0.2)' : 'none',
                              flexShrink: 0,
                            }} />
                            <span style={{ fontSize: 9, color: active ? '#E8612D' : '#9CA3AF', whiteSpace: 'nowrap' }}>
                              {step}
                            </span>
                          </div>
                          {/* Connector line */}
                          {i < 2 && (
                            <div style={{
                              flex: 1, height: 2, margin: '0 4px',
                              marginBottom: 14,
                              background: past ? '#9CA3AF' : '#E5E7EB',
                            }} />
                          )}
                        </div>
                      )
                    })}
                  </div>

                  {/* Current status label */}
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                    <span style={{ fontSize: 11, color: '#9CA3AF' }}>Status</span>
                    <span style={{ fontSize: 15, fontWeight: 700, color: '#E8612D' }}>
                      {(data.kanban_stage || 'NEW').replace(/_/g, ' ')}
                    </span>
                  </div>
                </SectionCard>

                {/* 7. BOTTOM ACTION */}
                <div style={{ textAlign: 'center', paddingTop: 4 }}>
                  <button
                    onClick={() => navigate(`/complaint-detail/${data.id}`)}
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer',
                      fontSize: 13, fontWeight: 700, color: '#E8612D',
                      textDecoration: 'underline',
                    }}
                  >
                    View Full Details →
                  </button>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </>
  )
}

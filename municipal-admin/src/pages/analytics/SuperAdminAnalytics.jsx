/**
 * SuperAdminAnalytics — dark navy dashboard for super_admin role
 *
 * Sections:
 *   A — City Intelligence Cards (city-level KPIs + risk)
 *   B — National KPI strip + Charts (donut + funnel)
 *   C — AI Insight Cards (forecast, bottleneck, health)
 *   D — Predictive Alerts feed
 *
 * Each section is built module-by-module; placeholders shown until done.
 */
import { useState } from 'react'
import { SA } from './sa-theme'

const DAYS_OPTIONS = [7, 30, 90]

// ── Placeholder section card ─────────────────────────────────────────────────
function SectionPlaceholder({ label }) {
  return (
    <div
      style={{
        ...SA.cardStyle,
        padding: 32,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 160,
      }}
    >
      <p style={{ color: SA.muted, fontSize: 14, fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
        {label}
      </p>
    </div>
  )
}

// ── Days filter pill strip ───────────────────────────────────────────────────
function DaysFilter({ days, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 4, background: '#1C2A45', borderRadius: 10, padding: 4 }}>
      {DAYS_OPTIONS.map(d => (
        <button
          key={d}
          onClick={() => onChange(d)}
          style={{
            padding: '5px 14px',
            borderRadius: 7,
            border: 'none',
            cursor: 'pointer',
            fontSize: 13,
            fontWeight: 600,
            fontFamily: 'Plus Jakarta Sans, sans-serif',
            background: days === d ? SA.orange : 'transparent',
            color:      days === d ? '#fff'    : SA.muted,
            transition: 'all 0.15s',
          }}
        >
          {d}d
        </button>
      ))}
    </div>
  )
}

// ── Main page ────────────────────────────────────────────────────────────────
export default function SuperAdminAnalytics() {
  const [days, setDays] = useState(30)

  return (
    <div
      style={{
        minHeight: '100vh',
        background: SA.bg,
        fontFamily: 'Plus Jakarta Sans, sans-serif',
        color: SA.text,
      }}
    >
      {/* ── Header bar ── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '20px 28px',
          borderBottom: `1px solid ${SA.border}`,
          background: SA.card,
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 800, color: SA.text, letterSpacing: '-0.3px' }}>
            StreetLight-PK Super Admin Dashboard
          </h1>
          <p style={{ margin: '3px 0 0', fontSize: 13, color: SA.muted, fontWeight: 500 }}>
            City Intelligence &nbsp;·&nbsp; All Municipal Areas
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <DaysFilter days={days} onChange={setDays} />
        </div>
      </div>

      {/* ── Scrollable content ── */}
      <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 24 }}>

        {/* Section A — City Intelligence Cards */}
        <section>
          <SectionLabel letter="A" title="City Intelligence" sub="Per-city KPIs, risk ratings & drill-down" />
          <SectionPlaceholder label="Section A — coming in Module 2" />
        </section>

        {/* Section B — National KPIs + Charts */}
        <section>
          <SectionLabel letter="B" title="National Overview" sub="Aggregate KPIs · Issue breakdown · Pipeline" />
          <SectionPlaceholder label="Section B — coming in Module 3" />
        </section>

        {/* Section C — AI Insight Cards */}
        <section>
          <SectionLabel letter="C" title="AI Insights" sub="Forecast · Bottleneck signal · Citizen health index" />
          <SectionPlaceholder label="Section C — coming in Module 4" />
        </section>

        {/* Section D — Predictive Alerts */}
        <section>
          <SectionLabel letter="D" title="Predictive Alerts" sub="Rule-based signals · Area warnings · Anomalies" />
          <SectionPlaceholder label="Section D — coming in Module 5" />
        </section>

      </div>
    </div>
  )
}

// ── Section label helper ─────────────────────────────────────────────────────
function SectionLabel({ letter, title, sub }) {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 14 }}>
      <span
        style={{
          background: SA.orange,
          color: '#fff',
          fontSize: 11,
          fontWeight: 800,
          padding: '2px 7px',
          borderRadius: 5,
          letterSpacing: '0.5px',
        }}
      >
        {letter}
      </span>
      <span style={{ fontSize: 15, fontWeight: 700, color: SA.text }}>{title}</span>
      <span style={{ fontSize: 12, color: SA.muted }}>{sub}</span>
    </div>
  )
}

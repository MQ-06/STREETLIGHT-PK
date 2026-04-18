/**
 * SuperAdminAnalytics — Super Admin dashboard (warm beige design system)
 *
 * Sections:
 *   A — City-Wide KPI Strip
 *   B — National Charts (donut + funnel)
 *   C — AI Insight Cards
 *   D — Predictive Alerts feed
 */
import { useState } from 'react'
import SectionA from './sa/SectionA'

const DAYS_OPTIONS = [7, 30, 90]

// ── Placeholder ───────────────────────────────────────────────────────────────
function SectionPlaceholder({ label }) {
  return (
    <div className="bg-white rounded-2xl border border-warm-border p-8 flex items-center justify-center min-h-40">
      <p className="text-sm text-gray-400">{label}</p>
    </div>
  )
}

// ── Section label ─────────────────────────────────────────────────────────────
function SectionLabel({ letter, title, sub }) {
  return (
    <div className="flex items-baseline gap-2 mb-4">
      <span className="bg-primary text-white text-xs font-black px-2 py-0.5 rounded-md tracking-wide">
        {letter}
      </span>
      <span className="text-base font-bold text-gray-900">{title}</span>
      <span className="text-xs text-gray-400">{sub}</span>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function SuperAdminAnalytics() {
  const [days, setDays] = useState(30)

  return (
    <div className="p-6 space-y-6">

      {/* ── Page header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-gray-900">Super Admin Dashboard</h1>
          <p className="text-sm text-gray-400 mt-0.5">City Intelligence &nbsp;·&nbsp; All Municipal Areas</p>
        </div>

        {/* Days filter */}
        <div className="flex gap-1 bg-white border border-warm-border rounded-xl p-1">
          {DAYS_OPTIONS.map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors ${
                days === d ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-800'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* ── Section A — City-Wide KPI Strip ── */}
      <section>
        <SectionLabel
          letter="A"
          title="City Intelligence"
          sub="City-wide aggregate KPIs across all municipal areas"
        />
        <SectionA days={days} />
      </section>

      {/* ── Section B — National Charts ── */}
      <section>
        <SectionLabel
          letter="B"
          title="National Overview"
          sub="Issue breakdown · Pipeline lifecycle"
        />
        <SectionPlaceholder label="Section B — coming in Module 3" />
      </section>

      {/* ── Section C — AI Insights ── */}
      <section>
        <SectionLabel
          letter="C"
          title="AI Insights"
          sub="Forecast · Bottleneck signal · Citizen health index"
        />
        <SectionPlaceholder label="Section C — coming in Module 4" />
      </section>

      {/* ── Section D — Predictive Alerts ── */}
      <section>
        <SectionLabel
          letter="D"
          title="Predictive Alerts"
          sub="Rule-based signals · Area warnings · Anomalies"
        />
        <SectionPlaceholder label="Section D — coming in Module 5" />
      </section>

    </div>
  )
}

// Module 2 — Fetches issue-breakdown + pipeline, renders side-by-side
import { useState, useEffect } from 'react'
import { authFetch } from '../../utils/auth'
import DonutChart     from './DonutChart'
import PipelineFunnel from './PipelineFunnel'

function CardSkeleton() {
  return <div className="bg-white rounded-2xl border border-warm-border h-64 animate-pulse" />
}

export default function ChartRow({ scope, scopeId, days }) {
  const [breakdown, setBreakdown] = useState(null)
  const [pipeline,  setPipeline]  = useState(null)
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    const params = new URLSearchParams({ scope, scope_id: scopeId || '', days })

    Promise.all([
      authFetch(`/admin/analytics/issue-breakdown?${params}`).then(r => r.json()),
      authFetch(`/admin/analytics/pipeline?${params}`).then(r => r.json()),
    ])
      .then(([bd, pl]) => {
        if (!cancelled) { setBreakdown(bd); setPipeline(pl); setLoading(false) }
      })
      .catch(() => { if (!cancelled) setLoading(false) })

    return () => { cancelled = true }
  }, [scope, scopeId, days])

  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-4">
        <CardSkeleton /><CardSkeleton />
      </div>
    )
  }

  if (!breakdown || !pipeline) return null

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="bg-white rounded-2xl border border-warm-border p-5">
        <DonutChart data={breakdown.breakdown} title="Issue Type Breakdown" />
      </div>
      <div className="bg-white rounded-2xl border border-warm-border p-5">
        <PipelineFunnel
          stages={pipeline.stages}
          bottleneck={pipeline.bottleneck_stage}
          title="Report Pipeline"
        />
      </div>
    </div>
  )
}

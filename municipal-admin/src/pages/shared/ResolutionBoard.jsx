import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { RefreshCw, ExternalLink, MapPin } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { authFetch } from '../../utils/auth'
import { useAdminSearch } from '../../context/AdminSearchContext'
import { STAGE_MAP } from '../../utils/theme'

const STAGES = [
  { key: 'NEW',                  label: 'New',                 color: '#6B7280' },
  { key: 'PENDING_VERIFICATION', label: 'Pending Verification',color: '#3B82F6' },
  { key: 'VERIFIED',             label: 'Verified',            color: '#F97316' },
  { key: 'IN_PROGRESS',         label: 'In Progress',         color: '#F59E0B' },
  { key: 'AWAITING_FEEDBACK',    label: 'Awaiting Feedback',   color: '#8B5CF6' },
  { key: 'RESOLVED',             label: 'Resolved',            color: '#22C55E' },
  { key: 'CLOSED',               label: 'Closed',              color: '#64748B' },
]

const SEV_STYLE = {
  high:   { bg: '#FEF2F2', color: '#EF4444' },
  large:  { bg: '#FEF2F2', color: '#EF4444' },
  medium: { bg: '#FFF7ED', color: '#F97316' },
  low:    { bg: '#F0FDF4', color: '#22C55E' },
  small:  { bg: '#F0FDF4', color: '#22C55E' },
}

function daysSince(iso) {
  if (!iso) return null
  const diff = Date.now() - new Date(iso).getTime()
  return Math.floor(diff / 86400000)
}

function KanbanCard({ card, index, navigate }) {
  const sev  = (card.severity || 'medium').toLowerCase()
  const days = daysSince(card.created_at)
  const s    = SEV_STYLE[sev] || SEV_STYLE.medium

  return (
    <Draggable draggableId={String(card.id)} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className="bg-white rounded-2xl p-4 mb-2 shadow-sm border border-warm-border select-none"
          style={{
            ...provided.draggableProps.style,
            opacity: snapshot.isDragging ? 0.9 : 1,
            boxShadow: snapshot.isDragging ? '0 8px 24px rgba(0,0,0,0.12)' : undefined,
          }}
        >
          <div className="flex items-start justify-between gap-2 mb-2">
            <span className="text-xs font-black text-gray-500">{card.display_id}</span>
            <span
              className="text-xs font-bold px-2 py-0.5 rounded-full shrink-0"
              style={{ backgroundColor: s.bg, color: s.color }}
            >
              {card.severity}
            </span>
          </div>
          <p className="text-sm font-semibold text-gray-800 leading-snug mb-1 line-clamp-2">{card.title}</p>
          {card.location && (
            <p className="text-xs text-gray-400 mb-2 truncate flex items-center gap-1">
              <MapPin size={10} className="shrink-0" />{card.location}
            </p>
          )}
          <div className="flex items-center justify-between">
            {days !== null && (
              <span className={`text-xs font-medium ${days > 3 ? 'text-red-500' : 'text-gray-400'}`}>
                {days === 0 ? 'Today' : days + 'd ago'}
              </span>
            )}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                navigate('/complaint-detail/' + card.id)
              }}
              className="text-primary hover:underline text-xs font-bold flex items-center gap-1"
            >
              View <ExternalLink size={10} />
            </button>
          </div>
        </div>
      )}
    </Draggable>
  )
}

export default function ResolutionBoard() {
  const navigate = useNavigate()
  const { query: searchQuery } = useAdminSearch()
  const [columns, setColumns]   = useState(() =>
    Object.fromEntries(STAGES.map(s => [s.key, []]))
  )
  const [loading, setLoading]   = useState(true)
  const [error,   setError]     = useState(null)
  const [moving,  setMoving]    = useState(null)  // report id being moved

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (searchQuery.trim()) params.set('search', searchQuery.trim())
      const qs = params.toString()
      const res  = await authFetch('/admin/reports/kanban' + (qs ? `?${qs}` : ''))
      if (!res.ok) throw new Error('kanban ' + res.status)
      const data = await res.json()
      const map  = {}
      for (const col of data.columns || []) map[col.stage] = col.cards
      setColumns(prev => ({ ...prev, ...map }))
    } catch {
      setError('Failed to load board.')
    } finally {
      setLoading(false)
    }
  }, [searchQuery])

  useEffect(() => { load() }, [load])

  async function onDragEnd(result) {
    const { source, destination, draggableId } = result
    if (!destination || destination.droppableId === source.droppableId) return

    const srcKey  = source.droppableId
    const dstKey  = destination.droppableId
    const reportId = parseInt(draggableId)

    // Optimistic update
    setColumns(prev => {
      const srcCards = [...(prev[srcKey] || [])]
      const dstCards = [...(prev[dstKey] || [])]
      const [moved]  = srcCards.splice(source.index, 1)
      dstCards.splice(destination.index, 0, { ...moved, kanban_stage: dstKey })
      return { ...prev, [srcKey]: srcCards, [dstKey]: dstCards }
    })

    setMoving(reportId)
    try {
      const res = await authFetch('/admin/reports/' + reportId + '/stage', {
        method: 'PATCH',
        body: JSON.stringify({ stage: dstKey }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        console.warn('Stage update failed:', err.detail || res.status)
        load()
      }
    } catch {
      load()
    } finally {
      setMoving(null)
    }
  }

  const totalCards = Object.values(columns).reduce((sum, c) => sum + c.length, 0)

  return (
    <div className="p-6 flex flex-col gap-5 h-full">
      <PageHeader
        title="Resolution Board"
        subtitle={
          searchQuery.trim()
            ? `Filtered by search · ${totalCards} matching cards`
            : 'Drag complaints across stages to update their status.'
        }
      >
        <span className="text-sm text-gray-500">{totalCards} total</span>
        <button
          onClick={load}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-warm-border text-sm font-semibold text-gray-600 hover:bg-gray-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </PageHeader>

      {error && <p className="text-sm text-red-500">{error}</p>}

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-sm text-gray-400">Loading board…</div>
      ) : (
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: 500 }}>
            {STAGES.map(stage => {
              const cards = columns[stage.key] || []
              return (
                <div key={stage.key} className="flex flex-col shrink-0" style={{ width: 260 }}>
                  {/* Column header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: stage.color }} />
                      <span className="text-xs font-bold text-gray-700 uppercase tracking-wide">
                        {stage.label}
                      </span>
                    </div>
                    <span
                      className="text-xs font-black px-2 py-0.5 rounded-full"
                      style={{ backgroundColor: stage.color + '20', color: stage.color }}
                    >
                      {cards.length}
                    </span>
                  </div>

                  {/* Droppable zone */}
                  <Droppable droppableId={stage.key}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        className="flex-1 rounded-2xl p-2 transition-colors min-h-24"
                        style={{
                          backgroundColor: snapshot.isDraggingOver ? stage.color + '10' : '#F7F6E8',
                          border: snapshot.isDraggingOver ? '2px dashed ' + stage.color : '2px dashed transparent',
                        }}
                      >
                        {cards.length === 0 && !snapshot.isDraggingOver && (
                          <div className="flex items-center justify-center h-20 text-xs text-gray-400">
                            Drop here
                          </div>
                        )}
                        {cards.map((card, idx) => (
                          <KanbanCard
                            key={card.id}
                            card={card}
                            index={idx}
                            navigate={navigate}
                          />
                        ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </div>
              )
            })}
          </div>
        </DragDropContext>
      )}
    </div>
  )
}

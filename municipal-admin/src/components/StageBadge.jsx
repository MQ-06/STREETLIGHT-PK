import { STAGE_MAP } from '../utils/theme'

/**
 * StageBadge — colored pill for a kanban stage.
 * Props: stage (string), size ('sm' | 'md')
 */
export default function StageBadge({ stage, size = 'md' }) {
  const s = STAGE_MAP[stage] || STAGE_MAP['NEW']
  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-xs'

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full ${px}`}
      style={{ backgroundColor: s.bg, color: s.text }}
    >
      <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: s.dot }} />
      {s.label}
    </span>
  )
}

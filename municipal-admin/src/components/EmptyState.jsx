/**
 * EmptyState — placeholder for pages not yet implemented.
 *
 * Props:
 *   icon        string   — emoji
 *   title       string
 *   description string
 *   phase       number   — e.g. 3 → "Coming in Phase 3"
 */
export default function EmptyState({ icon = '🚧', title, description, phase }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center py-24 gap-4 text-center">
      <div
        className="w-20 h-20 rounded-3xl flex items-center justify-center text-4xl shadow-sm"
        style={{ backgroundColor: '#FFF3EB' }}
      >
        {icon}
      </div>
      <div>
        <h2 className="text-xl font-extrabold text-gray-900">{title}</h2>
        {description && (
          <p className="text-sm text-gray-500 mt-1 max-w-sm mx-auto leading-relaxed">{description}</p>
        )}
        {phase && (
          <span
            className="inline-block mt-3 text-xs font-bold px-3 py-1.5 rounded-full"
            style={{ backgroundColor: '#FFF3EB', color: '#B85C2E' }}
          >
            Coming in Phase {phase}
          </span>
        )}
      </div>
    </div>
  )
}

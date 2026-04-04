/**
 * PageHeader — consistent page title + subtitle + optional action slot.
 *
 * Props:
 *   title     string
 *   subtitle  string
 *   children  ReactNode  — action buttons (optional)
 */
export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-black text-gray-900 tracking-tight">{title}</h1>
        {subtitle && (
          <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>
        )}
      </div>
      {children && (
        <div className="flex items-center gap-3 shrink-0">
          {children}
        </div>
      )}
    </div>
  )
}

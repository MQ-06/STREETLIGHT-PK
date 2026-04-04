import PageHeader from '../../components/PageHeader'
import EmptyState from '../../components/EmptyState'

export default function ResolutionBoard() {
  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Resolution Board" subtitle="Kanban-style complaint workflow management." />
      <EmptyState icon="📋" title="Resolution Board" description="Drag-and-drop Kanban board to move complaints through workflow stages." phase={3} />
    </div>
  )
}

import PageHeader from '../../components/PageHeader'
import EmptyState from '../../components/EmptyState'

export default function Transparency() {
  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Transparency Portal" subtitle="Public-facing performance metrics and accountability reports." />
      <EmptyState icon="📊" title="Transparency Portal" description="Publish resolution rates, average response times, and department performance to citizens." phase={3} />
    </div>
  )
}

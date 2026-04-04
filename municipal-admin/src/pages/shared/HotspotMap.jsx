import PageHeader from '../../components/PageHeader'
import EmptyState from '../../components/EmptyState'

export default function HotspotMap() {
  return (
    <div className="p-6 flex flex-col gap-6">
      <PageHeader title="Hotspot Map" subtitle="Geographic heatmap of reported civic issues." />
      <EmptyState icon="🗺️" title="Live Hotspot Map" description="Interactive map showing complaint density and recurring problem areas across the city." phase={3} />
    </div>
  )
}

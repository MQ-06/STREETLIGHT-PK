function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-md flex flex-col">
      <div className="h-16 flex items-center justify-center border-b">
        <span className="text-xl font-bold text-blue-700">MunicipalAdmin</span>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        <p className="text-xs text-gray-400 uppercase tracking-wide mb-3">Navigation</p>
      </nav>
    </aside>
  )
}

export default Sidebar

function Navbar() {
  return (
    <header className="h-16 bg-white shadow-sm flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-gray-700">Municipal & Admin Portal</h1>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-500">Admin User</span>
      </div>
    </header>
  )
}

export default Navbar

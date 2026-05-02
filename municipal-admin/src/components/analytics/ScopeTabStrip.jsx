/**
 * Module 5 — ScopeTabStrip
 *
 * Renders one or two rows of tabs so the user can switch analytics scope:
 *
 *  dept_officer → no tabs (fixed single scope)
 *  city_admin   → one row: [All Departments] [Dept A] [Dept B] …
 *  super_admin  → two rows:
 *                  Row 1: [National] [City A] [City B] …
 *                  Row 2: [All Depts] [Dept A] [Dept B] … (only when a city is selected)
 *
 * Calls onSelect(scope, scopeId) when the active tab changes.
 */
import { useState, useEffect } from 'react'
import { authFetchJson, getRole, getCity } from '../../utils/auth'

function Tab({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-1.5 rounded-lg text-sm font-semibold whitespace-nowrap border transition-colors ${
        active
          ? 'bg-primary text-white border-primary shadow-sm'
          : 'bg-white text-gray-500 border-warm-border hover:border-primary hover:text-gray-800'
      }`}
    >
      {label}
    </button>
  )
}

export default function ScopeTabStrip({ onSelect, forcedCity = undefined }) {
  const role = getRole()
  const city = getCity()

  const [scopes,      setScopes]      = useState(null)
  const [activeCity,  setActiveCity]  = useState(null)   // null = national (super_admin) or fixed city
  const [activeDept,  setActiveDept]  = useState(null)   // null = "all depts"

  // Sync when parent forces a city selection (e.g. city card click)
  useEffect(() => {
    if (forcedCity !== undefined) {
      setActiveCity(forcedCity)
      setActiveDept(null)
    }
  }, [forcedCity])

  // Fetch available scopes once on mount
  useEffect(() => {
    authFetchJson('/admin/analytics/scopes')
      .then(d => {
        setScopes(d)
        // Set sensible defaults
        if (role === 'city_admin') {
          setActiveCity(city)
          setActiveDept(null)   // "all depts" selected by default
        }
        // super_admin starts at national (activeCity = null)
        // dept_officer: no tabs shown
      })
      .catch(() => {})
  }, [])

  // Fire onSelect whenever active city/dept changes
  useEffect(() => {
    if (role === 'dept_officer') return   // handled by parent default scope

    if (role === 'city_admin') {
      if (activeDept) {
        onSelect('city_dept', `${activeCity}_${activeDept}`)
      } else {
        onSelect('city', activeCity || '')
      }
      return
    }

    // super_admin
    if (!activeCity) {
      onSelect('national', '')
    } else if (activeDept) {
      onSelect('city_dept', `${activeCity}_${activeDept}`)
    } else {
      onSelect('city', activeCity)
    }
  }, [activeCity, activeDept])

  // dept_officer has no tabs — parent already has their fixed scope
  if (role === 'dept_officer' || !scopes) return null

  const cities  = scopes.cities  || []
  const deptMap = scopes.departments || {}
  const depts   = activeCity ? (deptMap[activeCity] || []) : []

  return (
    <div className="flex flex-col gap-2">
      {/* ── City / National row ── */}
      {role === 'super_admin' && (
        <div className="flex gap-2 flex-wrap">
          <Tab
            label="National"
            active={activeCity === null}
            onClick={() => { setActiveCity(null); setActiveDept(null) }}
          />
          {cities.map(c => (
            <Tab
              key={c.id}
              label={c.label}
              active={activeCity === c.id}
              onClick={() => { setActiveCity(c.id); setActiveDept(null) }}
            />
          ))}
        </div>
      )}

      {/* ── Department row ── (city_admin always; super_admin only when a city is selected) */}
      {(role === 'city_admin' || (role === 'super_admin' && activeCity)) && depts.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <Tab
            label="All Departments"
            active={activeDept === null}
            onClick={() => setActiveDept(null)}
          />
          {depts.map(d => (
            <Tab
              key={d.id}
              label={d.label}
              active={activeDept === d.id}
              onClick={() => setActiveDept(d.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api/client'
import { RestaurantCard } from '../components/RestaurantCard'
import { useAuth } from '../context/AuthContext'
import type { Restaurant } from '../types'

type Filters = {
  search: string
  veg: boolean
  open: boolean
  sort: '' | 'rating' | 'delivery_time'
}

export function HomePage() {
  const { state: auth } = useAuth()
  const [restaurants, setRestaurants] = useState<Restaurant[] | null>(null)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState<Filters>({ search: '', veg: false, open: false, sort: '' })
  const [searchInput, setSearchInput] = useState('')

  const params = useMemo(
    () => ({
      search: filters.search || undefined,
      veg: filters.veg || undefined,
      open: filters.open || undefined,
      sort: filters.sort || undefined,
    }),
    [filters],
  )

  useEffect(() => {
    let active = true
    api
      .restaurants(params)
      .then((data) => {
        if (active) setRestaurants(data.results)
      })
      .catch((err: Error) => {
        if (active) setError(err.message)
      })
    return () => {
      active = false
    }
  }, [params])

  const onSearchSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    setFilters((current) => ({ ...current, search: searchInput.trim() }))
  }

  return (
    <div className="page">
      <section className="hero">
        <h1 className="hero__title">
          Hungry? <span className="hero__accent">Order in 30 minutes.</span>
        </h1>
        <p className="hero__subtitle">
          Fresh food from the best kitchens around you, delivered hot.
        </p>
        {auth.status === 'authenticated' && (
          <p className="hero__hello">Hi {auth.user.name.split(' ')[0]} 👋 what are you craving today?</p>
        )}
      </section>

      <section className="toolbar">
        <form className="search" onSubmit={onSearchSubmit} role="search">
          <span className="search__icon" aria-hidden="true">
            🔍
          </span>
          <input
            className="search__input"
            type="search"
            placeholder="Search restaurants or cuisines…"
            value={searchInput}
            onChange={(event) => setSearchInput(event.target.value)}
            aria-label="Search restaurants"
          />
          {filters.search && (
            <button
              type="button"
              className="search__clear"
              onClick={() => {
                setSearchInput('')
                setFilters((current) => ({ ...current, search: '' }))
              }}
            >
              Clear
            </button>
          )}
        </form>

        <div className="toolbar__filters">
          <button
            type="button"
            className={`toggle ${filters.veg ? 'toggle--active' : ''}`}
            onClick={() => setFilters((c) => ({ ...c, veg: !c.veg }))}
          >
            🟢 Pure Veg
          </button>
          <button
            type="button"
            className={`toggle ${filters.open ? 'toggle--active' : ''}`}
            onClick={() => setFilters((c) => ({ ...c, open: !c.open }))}
          >
            🟢 Open Now
          </button>
          <select
            className="select"
            value={filters.sort}
            onChange={(event) =>
              setFilters((c) => ({ ...c, sort: event.target.value as Filters['sort'] }))
            }
            aria-label="Sort restaurants"
          >
            <option value="">Sort: Relevance</option>
            <option value="rating">Rating: High → Low</option>
            <option value="delivery_time">Delivery: Fastest</option>
          </select>
        </div>
      </section>

      {error && <div className="banner banner--error">{error}</div>}

      {restaurants === null && !error && (
        <div className="grid">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="card card--skeleton" />
          ))}
        </div>
      )}

      {restaurants !== null && restaurants.length === 0 && (
        <div className="banner banner--empty">
          <p>No restaurants matched your filters. 🍽️</p>
          <Link to="/">Reset filters</Link>
        </div>
      )}

      {restaurants !== null && restaurants.length > 0 && (
        <>
          <p className="grid__count">
            {restaurants.length} restaurant{restaurants.length > 1 ? 's' : ''} delivering to you
          </p>
          <div className="grid">
            {restaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

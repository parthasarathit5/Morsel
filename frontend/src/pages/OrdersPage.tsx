import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from '../api/client'
import { Price } from '../components/Price'
import { useAuth } from '../context/AuthContext'
import type { Order } from '../types'

export function OrdersPage() {
  const { state: auth } = useAuth()
  const [orders, setOrders] = useState<Order[] | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (auth.status !== 'authenticated') return
    let active = true
    api
      .myOrders()
      .then((data) => {
        if (active) setOrders(data.results)
      })
      .catch((err: Error) => {
        if (active) setError(err.message)
      })
    return () => {
      active = false
    }
  }, [auth.status])

  if (auth.status === 'loading') return <div className="page" />

  if (auth.status === 'anonymous') {
    return (
      <div className="page page--narrow">
        <div className="auth-card">
          <h1 className="auth-card__title">Your orders 📦</h1>
          <p className="auth-card__subtitle">Log in to see your order history.</p>
          <Link to="/login" state={{ from: '/orders' }} className="btn btn--primary btn--full">
            Log in
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <h1 className="section-title">My Orders</h1>

      {error && <div className="banner banner--error">{error}</div>}

      {orders === null && !error && (
        <div className="order-list order-list--skeleton">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="order-card order-card--skeleton" />
          ))}
        </div>
      )}

      {orders !== null && orders.length === 0 && (
        <div className="banner banner--empty">
          <p>No orders yet 🍽️ Time for your first feast!</p>
          <Link to="/">Browse restaurants</Link>
        </div>
      )}

      {orders !== null && orders.length > 0 && (
        <div className="order-list">
          {orders.map((order) => (
            <Link key={order.id} to={`/order/${order.id}`} className="order-card">
              <div className="order-card__head">
                <span className="order-card__emoji">{order.restaurant_emoji ?? '🍽️'}</span>
                <div className="order-card__title">
                  <strong>{order.restaurant_name}</strong>
                  <span className="order-card__items">{order.first_items}</span>
                </div>
                <span className={`status-pill status-pill--${order.status}`}>
                  {order.status.replaceAll('_', ' ')}
                </span>
              </div>
              <div className="order-card__foot">
                <span>
                  {order.item_count} item{order.item_count === 1 ? '' : 's'} ·{' '}
                  <Price value={order.grand_total} />
                </span>
                <span className="order-card__view">View details →</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

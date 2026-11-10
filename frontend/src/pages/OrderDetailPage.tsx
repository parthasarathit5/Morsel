import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { api } from '../api/client'
import { Price } from '../components/Price'
import { useCart } from '../context/CartContext'
import type { Order } from '../types'

const TRACK_STEPS = [
  { key: 'placed', label: 'Order placed', icon: '🧾' },
  { key: 'preparing', label: 'Preparing your food', icon: '👨‍🍳' },
  { key: 'out_for_delivery', label: 'Out for delivery', icon: '🛵' },
  { key: 'delivered', label: 'Delivered', icon: '🎉' },
] as const

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { clear } = useCart()
  const [order, setOrder] = useState<Order | null>(null)
  const [error, setError] = useState('')
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const load = useCallback(async () => {
    try {
      setOrder(await api.order(id!))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load order')
    }
  }, [id])

  useEffect(() => {
    void load()
  }, [load])

  // Poll while the order is actively progressing (Swiggy-style live tracking).
  useEffect(() => {
    if (!order || !['placed', 'preparing', 'out_for_delivery'].includes(order.status)) return
    pollRef.current = setInterval(() => void load(), 8000)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [order, load])

  if (error) {
    return (
      <div className="page">
        <div className="banner banner--error">{error}</div>
        <Link to="/orders">← My orders</Link>
      </div>
    )
  }

  if (!order) {
    return (
      <div className="page">
        <div className="order-card order-card--skeleton" />
      </div>
    )
  }

  const activeIndex = TRACK_STEPS.findIndex((step) => step.key === order.status)
  const cancelled = order.status === 'cancelled'
  const canAdvance = ['placed', 'preparing', 'out_for_delivery'].includes(order.status)
  const canCancel = ['placed', 'preparing'].includes(order.status)

  const onAdvance = async () => {
    try {
      setOrder(await api.advanceOrder(order.id))
    } catch {
      /* order may have already moved on — next poll will fix it */
    }
  }

  const onCancel = async () => {
    if (!window.confirm('Cancel this order?')) return
    try {
      setOrder(await api.cancelOrder(order.id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Cancel failed')
    }
  }

  const onReorder = () => {
    clear()
    navigate('/')
  }

  return (
    <div className="page page--narrow">
      <Link to="/orders" className="back-link">
        ← My orders
      </Link>

      <header className="order-hero">
        <span className="order-hero__emoji">{order.restaurant_emoji ?? '🍽️'}</span>
        <div>
          <h1 className="order-hero__title">{order.restaurant_name}</h1>
          <p className="order-hero__sub">
            Order #{order.id} · {order.items?.length ?? 0} item
            {(order.items?.length ?? 0) === 1 ? '' : 's'} ·{' '}
            <Price value={order.grand_total} />
          </p>
          <p className="order-hero__sub order-hero__sub--dim">
            Placed {new Date(order.created_at).toLocaleString()}
          </p>
        </div>
        <span className={`status-pill status-pill--${order.status}`}>
          {order.status.replaceAll('_', ' ')}
        </span>
      </header>

      {!cancelled && order.payment && (
        <section className="track card-flat">
          <h2 className="section-title">Live tracking</h2>
          <div className="track__steps">
            {TRACK_STEPS.map((step, index) => {
              const state = index < activeIndex ? 'done' : index === activeIndex ? 'active' : 'todo'
              return (
                <div key={step.key} className={`track__step track__step--${state}`}>
                  <span className="track__icon">{step.icon}</span>
                  <span className="track__label">{step.label}</span>
                  {state === 'active' && index < TRACK_STEPS.length - 1 && (
                    <span className="track__pulse" aria-label="In progress" />
                  )}
                </div>
              )
            })}
          </div>

          <div className="track__actions">
            {canAdvance && (
              <button type="button" className="btn btn--ghost" onClick={() => void onAdvance()}>
                Simulate next stage (demo)
              </button>
            )}
            {canCancel && (
              <button type="button" className="btn btn--danger-ghost" onClick={() => void onCancel()}>
                Cancel order
              </button>
            )}
            {order.status === 'delivered' && (
              <button type="button" className="btn btn--primary" onClick={onReorder}>
                Order again 🍽️
              </button>
            )}
          </div>
        </section>
      )}

      <section className="card-flat">
        <h2 className="section-title">Items</h2>
        <div className="bill__lines">
          {order.items?.map((item) => (
            <div key={item.id} className="bill__line">
              <span className="bill__line-name">
                {item.emoji} {item.name} × {item.quantity}
              </span>
              <span>
                <Price value={item.total} />
              </span>
            </div>
          ))}
        </div>
        <div className="bill__totals">
          <div className="bill__row">
            <span>Item total</span>
            <span>
              <Price value={order.items_total ?? 0} />
            </span>
          </div>
          <div className="bill__row">
            <span>Delivery fee</span>
            <span>
              <Price value={order.delivery_fee ?? 0} />
            </span>
          </div>
          <div className="bill__row">
            <span>Taxes & fees</span>
            <span>
              <Price value={order.taxes ?? 0} />
            </span>
          </div>
          <div className="bill__row bill__row--total">
            <span>Total paid</span>
            <span>
              <Price value={order.grand_total} />
            </span>
          </div>
        </div>
      </section>

      <section className="card-flat">
        <h2 className="section-title">Delivery to</h2>
        <p className="address-block">
          <strong>{order.delivery_name}</strong> · {order.delivery_phone}
          <br />
          {order.delivery_address}
        </p>
        {order.payment && (
          <p className="payment-block">
            Paid via <strong>{order.payment.provider}</strong>
            {order.payment.demo && ' (demo mode)'} · ref{' '}
            <code>{order.payment.razorpay_payment_id || '—'}</code>
          </p>
        )}
      </section>
    </div>
  )
}

export function OrderSuccessPage() {
  const { id } = useParams<{ id: string }>()
  return (
    <div className="page page--narrow">
      <div className="success">
        <span className="success__emoji" role="img" aria-label="Success">
          🎉
        </span>
        <h1 className="success__title">Order confirmed!</h1>
        <p className="success__sub">
          Your food is on its way. We&apos;ll notify you at every step.
        </p>
        <Link to={`/order/${id}`} className="btn btn--primary btn--full">
          Track your order →
        </Link>
        <Link to="/" className="success__secondary">
          Continue browsing
        </Link>
      </div>
    </div>
  )
}

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { api } from '../api/client'
import { VegDot } from '../components/Badges'
import { Price } from '../components/Price'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import type { CheckoutResponse } from '../types'

/** Loads the official Razorpay Checkout script once. Returns window.Razorpay. */
function loadRazorpay(): Promise<typeof window.Razorpay | null> {
  return new Promise((resolve) => {
    if (typeof window === 'undefined') return resolve(null)
    if (window.Razorpay) return resolve(window.Razorpay)
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve(window.Razorpay ?? null)
    script.onerror = () => resolve(null)
    document.body.appendChild(script)
  })
}

export function CheckoutPage() {
  const navigate = useNavigate()
  const { state: auth } = useAuth()
  const { state: cart, lines, count, itemsTotal, deliveryFee, taxes, grandTotal, clear } = useCart()

  const [name, setName] = useState(auth.status === 'authenticated' ? auth.user.name : '')
  const [phone, setPhone] = useState(auth.status === 'authenticated' ? auth.user.phone : '')
  const [address, setAddress] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [stage, setStage] = useState<'form' | 'paying' | 'done'>('form')

  if (auth.status !== 'authenticated') {
    return (
      <div className="page page--narrow">
        <div className="auth-card">
          <h1 className="auth-card__title">Log in to checkout 🔒</h1>
          <p className="auth-card__subtitle">
            You need an account to place an order — it takes 30 seconds.
          </p>
          <Link to="/login" state={{ from: '/checkout' }} className="btn btn--primary btn--full">
            Log in
          </Link>
          <p className="auth-card__switch">
            New here? <Link to="/register">Create an account</Link>
          </p>
        </div>
      </div>
    )
  }

  if (count === 0 && stage === 'form') {
    return (
      <div className="page page--narrow">
        <div className="banner banner--empty">
          <p>Your cart is empty 🛒</p>
          <Link to="/">Browse restaurants</Link>
        </div>
      </div>
    )
  }

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    setStage('paying')

    try {
      // 1) Create the order on our server (prices validated server-side).
      const checkout: CheckoutResponse = await api.checkout({
        restaurant_id: cart.restaurantId!,
        items: lines.map((line) => ({ item_id: line.itemId, quantity: line.quantity })),
        delivery: { name: name.trim(), phone: phone.trim(), address: address.trim() },
      })

      // 2) Pay — via Razorpay Checkout when keys are configured,
      //    otherwise a simulated confirmation (demo mode).
      if (checkout.demo_mode) {
        await new Promise((resolve) => setTimeout(resolve, 1200)) // simulate gateway latency
        const order = await api.verifyPayment({ order_id: checkout.order_id })
        clear()
        navigate(`/order/${order.id}/success`, { replace: true })
      } else {
        const Razorpay = await loadRazorpay()
        if (!Razorpay) throw new Error('Could not load the Razorpay checkout script.')

        const rzp = new Razorpay({
          key: checkout.razorpay.key_id,
          order_id: checkout.razorpay.order_id,
          amount: checkout.amount_paise,
          currency: checkout.currency,
          name: 'FoodFlow',
          description: `Order from ${cart.restaurantName}`,
          prefill: { name: name.trim(), contact: phone.trim(), email: auth.user.email },
          theme: { color: '#f97316' },
          handler: async (response: {
            razorpay_order_id: string
            razorpay_payment_id: string
            razorpay_signature: string
          }) => {
            try {
              const order = await api.verifyPayment({
                order_id: checkout.order_id,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              })
              clear()
              navigate(`/order/${order.id}/success`, { replace: true })
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Payment verification failed')
              setStage('form')
            }
          },
          modal: {
            ondismiss: () => {
              setError('Payment cancelled. Your order is saved — you can retry.')
              setStage('form')
            },
          },
        })
        rzp.open()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Checkout failed')
      setStage('form')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page page--checkout">
      <Link to={`/restaurant/${cart.restaurantId}`} className="back-link">
        ← Back to {cart.restaurantName || 'restaurant'}
      </Link>

      <div className="checkout">
        <section className="checkout__main">
          <h1 className="section-title">Delivery details</h1>
          <form onSubmit={onSubmit} className="form">
            <label className="form__label">
              Name
              <input
                type="text"
                required
                minLength={2}
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Delivery contact name"
              />
            </label>

            <label className="form__label">
              Phone
              <input
                type="tel"
                required
                minLength={10}
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder="98765 43210"
              />
            </label>

            <label className="form__label">
              Delivery address
              <textarea
                required
                minLength={10}
                rows={3}
                value={address}
                onChange={(event) => setAddress(event.target.value)}
                placeholder="Flat / street / landmark…"
              />
            </label>

            {error && <p className="form__error">{error}</p>}

            <button
              type="submit"
              className="btn btn--primary btn--full"
              disabled={busy || stage === 'paying'}
            >
              {stage === 'paying' ? 'Processing…' : 'Proceed to payment'}
            </button>
            <p className="checkout__gateway">Payments secured by Razorpay · UPI / Cards / Netbanking</p>
          </form>
        </section>

        <aside className="checkout__bill">
          <h2 className="section-title">Bill from {cart.restaurantName}</h2>
          <div className="bill__lines">
            {lines.map((line) => (
              <div key={line.itemId} className="bill__line">
                <span className="bill__line-name">
                  <VegDot isVeg={line.is_veg} /> {line.emoji} {line.name} × {line.quantity}
                </span>
                <span>
                  <Price value={line.price * line.quantity} />
                </span>
              </div>
            ))}
          </div>

          <div className="bill__totals">
            <div className="bill__row">
              <span>Item total</span>
              <span>
                <Price value={itemsTotal} />
              </span>
            </div>
            <div className="bill__row">
              <span>Delivery fee {deliveryFee === 0 && '🎉'}</span>
              <span>
                {deliveryFee === 0 ? 'FREE' : <Price value={deliveryFee} />}
              </span>
            </div>
            <div className="bill__row">
              <span>GST (5%) + platform fee</span>
              <span>
                <Price value={taxes} />
              </span>
            </div>
            <div className="bill__row bill__row--total">
              <span>To pay</span>
              <span>
                <Price value={grandTotal} />
              </span>
            </div>
          </div>

          <div className="bill__note">
            Final prices are calculated by the server at checkout — your cart amounts are
            confirmed there.
          </div>
        </aside>
      </div>
    </div>
  )
}

import { Link } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import { Price } from './Price'

export function Navbar() {
  const { state: auth, logout } = useAuth()
  const { count, grandTotal, state: cart } = useCart()

  return (
    <header className="navbar">
      <div className="navbar__inner">
        <Link to="/" className="navbar__brand">
          <span className="navbar__logo">🍜</span>
          <span className="navbar__title">
            Food<span className="navbar__accent">Flow</span>
          </span>
        </Link>

        <nav className="navbar__links">
          <Link to="/orders" className="navbar__link">
            My Orders
          </Link>

          {auth.status === 'authenticated' ? (
            <div className="navbar__user">
              <span className="navbar__avatar">
                {auth.user.name.charAt(0).toUpperCase() || '?'}
              </span>
              <span className="navbar__username">{auth.user.name.split(' ')[0]}</span>
              <button
                type="button"
                className="navbar__logout"
                onClick={() => void logout()}
              >
                Log out
              </button>
            </div>
          ) : (
            <Link to="/login" className="navbar__link navbar__link--cta">
              Login
            </Link>
          )}
        </nav>
      </div>

      {count > 0 && (
        <div className="navbar__cart-strip">
          {cart.restaurantName} · {count} item{count > 1 ? 's' : ''} ·{' '}
          <Price value={grandTotal} /> — <Link to="/checkout">View cart →</Link>
        </div>
      )}
    </header>
  )
}

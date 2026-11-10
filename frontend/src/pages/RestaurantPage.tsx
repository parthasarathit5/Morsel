import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { api } from '../api/client'
import { MenuItemRow } from '../components/MenuItemRow'
import { RatingBadge } from '../components/Badges'
import { Price } from '../components/Price'
import { useCart } from '../context/CartContext'
import type { RestaurantDetail } from '../types'

export function RestaurantPage() {
  const { id } = useParams<{ id: string }>()
  const [restaurant, setRestaurant] = useState<RestaurantDetail | null>(null)
  const [error, setError] = useState('')
  const { addItem, setQuantity, quantityOf, count, grandTotal, state: cart } = useCart()

  useEffect(() => {
    let active = true
    api
      .restaurant(id!)
      .then((data) => {
        if (active) setRestaurant(data)
      })
      .catch((err: Error) => {
        if (active) setError(err.message)
      })
    return () => {
      active = false
    }
  }, [id])

  if (error) {
    return (
      <div className="page">
        <div className="banner banner--error">{error}</div>
        <Link to="/">← Back to restaurants</Link>
      </div>
    )
  }

  if (!restaurant) {
    return (
      <div className="page">
        <div className="detail detail--skeleton" />
      </div>
    )
  }

  const cartFromOtherRestaurant =
    cart.restaurantId !== null && cart.restaurantId !== restaurant.id

  return (
    <div className="page">
      <Link to="/" className="back-link">
        ← All restaurants
      </Link>

      <header className="detail" style={{ background: restaurant.gradient }}>
        <span className="detail__emoji" role="img" aria-label={restaurant.name}>
          {restaurant.emoji}
        </span>
        <div className="detail__info">
          <h1 className="detail__name">{restaurant.name}</h1>
          <p className="detail__cuisine">{restaurant.cuisine}</p>
          <p className="detail__address">{restaurant.address}</p>
          <div className="detail__meta">
            <RatingBadge rating={restaurant.rating} />
            <span>({restaurant.rating_count.toLocaleString()} ratings)</span>
            <span>•</span>
            <span>{restaurant.delivery_minutes} min delivery</span>
            <span>•</span>
            <span>
              <Price value={restaurant.price_for_two} /> for two
            </span>
          </div>
          {restaurant.offer_text && <p className="detail__offer">🎉 {restaurant.offer_text}</p>}
        </div>
        {!restaurant.is_open && <div className="detail__closed">Currently closed</div>}
      </header>

      {cartFromOtherRestaurant && (
        <div className="banner banner--warn">
          Your cart has items from <strong>{cart.restaurantName}</strong>. Adding from here will
          start a new cart.
        </div>
      )}

      <div className="menu">
        {restaurant.categories.map((category) => (
          <section key={category.id} className="menu__category">
            <h2 className="menu__category-title">
              {category.name} <span className="menu__category-count">({category.items.length})</span>
            </h2>
            <div className="menu__items">
              {category.items.map((item) => (
                <MenuItemRow
                  key={item.id}
                  item={item}
                  quantity={quantityOf(item.id)}
                  onAdd={() =>
                    addItem(
                      { id: restaurant.id, name: restaurant.name },
                      {
                        itemId: item.id,
                        name: item.name,
                        price: Number.parseFloat(item.price),
                        emoji: item.emoji,
                        is_veg: item.is_veg,
                      },
                    )
                  }
                  onRemove={() => setQuantity(item.id, quantityOf(item.id) - 1)}
                />
              ))}
            </div>
          </section>
        ))}
      </div>

      {count > 0 && !cartFromOtherRestaurant && (
        <div className="cart-dock">
          <div className="cart-dock__info">
            <strong>{count} item{count > 1 ? 's' : ''}</strong> · <Price value={grandTotal} />
          </div>
          <Link to="/checkout" className="btn btn--primary">
            View Cart →
          </Link>
        </div>
      )}
    </div>
  )
}

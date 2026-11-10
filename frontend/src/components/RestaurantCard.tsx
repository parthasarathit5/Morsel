import { Link } from 'react-router-dom'

import type { Restaurant } from '../types'
import { RatingBadge } from './Badges'
import { Price } from './Price'

export function RestaurantCard({ restaurant }: { restaurant: Restaurant }) {
  return (
    <Link to={`/restaurant/${restaurant.id}`} className={`card ${restaurant.is_open ? '' : 'card--closed'}`}>
      <div className="card__banner" style={{ background: restaurant.gradient }}>
        <span className="card__emoji" role="img" aria-label={restaurant.name}>
          {restaurant.emoji}
        </span>
        {restaurant.promoted && <span className="card__promoted">Promoted</span>}
      </div>

      <div className="card__body">
        <div className="card__head">
          <h3 className="card__name">{restaurant.name}</h3>
          {restaurant.offer_text && <span className="card__offer">{restaurant.offer_text}</span>}
        </div>

        <p className="card__cuisine">{restaurant.cuisine}</p>

        <div className="card__meta">
          <RatingBadge rating={restaurant.rating} />
          <span className="card__dot">•</span>
          <span>{restaurant.delivery_minutes} min</span>
          <span className="card__dot">•</span>
          <Price value={restaurant.price_for_two} />
        </div>

        <div className="card__foot">
          {restaurant.is_pure_veg && <span className="chip chip--veg">Pure Veg</span>}
          {restaurant.is_open ? (
            <span className="chip chip--open">Open now</span>
          ) : (
            <span className="chip chip--closed">Closed</span>
          )}
        </div>
      </div>
    </Link>
  )
}

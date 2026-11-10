import type { MenuItem } from '../types'
import { VegDot } from './Badges'
import { Price } from './Price'

type Props = {
  item: MenuItem
  quantity: number
  onAdd: () => void
  onRemove: () => void
}

export function MenuItemRow({ item, quantity, onAdd, onRemove }: Props) {
  return (
    <article className={`menu-item ${item.is_available ? '' : 'menu-item--disabled'}`}>
      <div className="menu-item__info">
        <div className="menu-item__title">
          <VegDot isVeg={item.is_veg} />
          <h4>{item.name}</h4>
          {item.is_bestseller && <span className="chip chip--bestseller">★ Bestseller</span>}
        </div>
        <p className="menu-item__price">
          <Price value={item.price} />
        </p>
        {item.description && <p className="menu-item__desc">{item.description}</p>}
      </div>

      <div className="menu-item__media">
        <span className="menu-item__emoji" role="img" aria-label={item.name}>
          {item.emoji}
        </span>
        {quantity === 0 ? (
          <button
            type="button"
            className="btn btn--add"
            disabled={!item.is_available}
            onClick={onAdd}
          >
            {item.is_available ? 'ADD +' : 'Unavailable'}
          </button>
        ) : (
          <div className="stepper">
            <button type="button" className="stepper__btn" onClick={onRemove} aria-label="Remove one">
              −
            </button>
            <span className="stepper__count">{quantity}</span>
            <button type="button" className="stepper__btn" onClick={onAdd} aria-label="Add one">
              +
            </button>
          </div>
        )}
      </div>
    </article>
  )
}

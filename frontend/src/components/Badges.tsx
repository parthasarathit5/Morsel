export function RatingBadge({ rating }: { rating: number | string }) {
  const value = typeof rating === 'string' ? Number.parseFloat(rating) : rating
  const excellent = value >= 4.5
  const good = value >= 4.0
  const className = excellent ? 'rating rating--excellent' : good ? 'rating rating--good' : 'rating rating--avg'
  return (
    <span className={className}>
      <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 21 12 17.77 5.82 21 7 14.14l-5-4.87 6.91-1.01L12 2z" />
      </svg>
      {value.toFixed(1)}
    </span>
  )
}

export function VegDot({ isVeg }: { isVeg: boolean }) {
  return (
    <span
      className={isVeg ? 'veg-dot veg-dot--veg' : 'veg-dot veg-dot--nonveg'}
      title={isVeg ? 'Veg' : 'Non-veg'}
      aria-label={isVeg ? 'Vegetarian' : 'Non-vegetarian'}
    >
      <span className="veg-dot__inner" />
    </span>
  )
}

/** Formats a number as Indian Rupees, e.g. 289 -> ₹289 */
export function Price({ value }: { value: number | string }) {
  const amount = typeof value === 'string' ? Number.parseFloat(value) : value
  if (!Number.isFinite(amount)) return <span>₹0</span>
  const formatted = amount % 1 === 0 ? amount.toString() : amount.toFixed(2)
  return <span>₹{formatted}</span>
}

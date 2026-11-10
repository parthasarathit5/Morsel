import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import type { CartLine } from '../types'

type CartState = {
  restaurantId: number | null
  restaurantName: string
  lines: CartLine[]
}

const EMPTY: CartState = { restaurantId: null, restaurantName: '', lines: [] }
const STORAGE_KEY = 'Foodiebay.cart'

type CartContextValue = {
  state: CartState
  lines: CartLine[]
  count: number
  itemsTotal: number
  deliveryFee: number
  taxes: number
  grandTotal: number
  quantityOf: (itemId: number) => number
  addItem: (
    restaurant: { id: number; name: string },
    line: Omit<CartLine, 'quantity'>,
  ) => void
  removeItem: (itemId: number) => void
  setQuantity: (itemId: number, quantity: number) => void
  clear: () => void
}

const CartContext = createContext<CartContextValue | null>(null)

function computeBill(state: CartState) {
  const itemsTotal = state.lines.reduce((sum, line) => sum + line.price * line.quantity, 0)
  const deliveryFee = itemsTotal === 0 || itemsTotal >= 149 ? 0 : 29
  const taxes = Math.round(itemsTotal * 0.05 * 100) / 100 + 6
  const grandTotal = itemsTotal === 0 ? 0 : itemsTotal + deliveryFee + taxes
  return { itemsTotal, deliveryFee, taxes, grandTotal }
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<CartState>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) return JSON.parse(raw) as CartState
    } catch {
      /* corrupted storage — start empty */
    }
    return EMPTY
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  }, [state])

  const quantityOf = useCallback(
    (itemId: number) => state.lines.find((line) => line.itemId === itemId)?.quantity ?? 0,
    [state.lines],
  )

  const addItem = useCallback<CartContextValue['addItem']>((restaurant, line) => {
    setState((current) => {
      const switchedRestaurant =
        current.restaurantId !== null && current.restaurantId !== restaurant.id
      const base = switchedRestaurant ? { ...EMPTY } : current
      const existing = base.lines.find((entry) => entry.itemId === line.itemId)
      const lines = existing
        ? base.lines.map((entry) =>
            entry.itemId === line.itemId
              ? { ...entry, quantity: Math.min(entry.quantity + 1, 20) }
              : entry,
          )
        : [...base.lines, { ...line, quantity: 1 }]
      return { restaurantId: restaurant.id, restaurantName: restaurant.name, lines }
    })
  }, [])

  const removeItem = useCallback((itemId: number) => {
    setState((current) => ({
      ...current,
      lines: current.lines.filter((line) => line.itemId !== itemId),
    }))
  }, [])

  const setQuantity = useCallback((itemId: number, quantity: number) => {
    setState((current) => {
      if (quantity <= 0) {
        return { ...current, lines: current.lines.filter((line) => line.itemId !== itemId) }
      }
      const lines = current.lines.map((line) =>
        line.itemId === itemId ? { ...line, quantity: Math.min(quantity, 20) } : line,
      )
      const next = { ...current, lines }
      return next.lines.length > 0 ? next : EMPTY
    })
  }, [])

  const clear = useCallback(() => setState(EMPTY), [])

  const bill = computeBill(state)

  const value = useMemo(
    () => ({
      state,
      lines: state.lines,
      count: state.lines.reduce((sum, line) => sum + line.quantity, 0),
      ...bill,
      quantityOf,
      addItem,
      removeItem,
      setQuantity,
      clear,
    }),
    [state, bill, quantityOf, addItem, removeItem, setQuantity, clear],
  )

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export function useCart(): CartContextValue {
  const context = useContext(CartContext)
  if (!context) throw new Error('useCart must be used inside <CartProvider>')
  return context
}

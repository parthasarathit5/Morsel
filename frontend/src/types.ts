export type User = {
  id: number
  email: string
  name: string
  phone: string
}

export type Restaurant = {
  id: number
  name: string
  cuisine: string
  rating: string
  rating_count: number
  delivery_minutes: number
  price_for_two: number
  is_pure_veg: boolean
  is_open: boolean
  promoted: boolean
  offer_text: string
  emoji: string
  gradient: string
}

export type MenuItem = {
  id: number
  name: string
  description: string
  price: string
  is_veg: boolean
  is_bestseller: boolean
  is_available: boolean
  emoji: string
  category: string
}

export type RestaurantDetail = Restaurant & {
  address: string
  categories: Array<{ id: number; name: string; items: MenuItem[] }>
}

export type CheckoutResponse = {
  order_id: number
  amount: number
  amount_paise: number
  currency: string
  demo_mode: boolean
  razorpay: { key_id: string; order_id: string }
  bill: { items_total: number; delivery_fee: number; taxes: number; grand_total: number }
}

export type OrderItem = {
  id: number
  name: string
  emoji: string
  is_veg: boolean
  price: string
  quantity: number
  total: string
}

export type Order = {
  id: number
  status: string
  restaurant_name?: string
  restaurant_emoji?: string
  item_count?: number
  first_items?: string
  grand_total: string
  created_at: string
  items?: OrderItem[]
  payment?: {
    provider: string
    razorpay_payment_id: string
    amount: number
    currency: string
    status: string
    demo: boolean
    paid_at: string | null
  }
  items_total?: string
  delivery_fee?: string
  taxes?: string
  delivery_name?: string
  delivery_phone?: string
  delivery_address?: string
  delivery_minutes?: number
}

export type CartLine = {
  itemId: number
  name: string
  price: number
  emoji: string
  is_veg: boolean
  quantity: number
}

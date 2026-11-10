import type { CheckoutResponse, Order, Restaurant, RestaurantDetail, User } from '../types'

/**
 * Base URL of the Foodiebay API.
 * - Local dev: '' (empty) — Vite proxies /api to 127.0.0.1:8000
 * - Firebase / APK: set VITE_API_BASE_URL=https://<your-render-app>.onrender.com
 */
export const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const TOKEN_KEY = 'Foodiebay.access'
const REFRESH_KEY = 'Foodiebay.refresh'

export const tokens = {
  get access() {
    return localStorage.getItem(TOKEN_KEY) ?? ''
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY) ?? ''
  },
  save(access: string, refresh?: string) {
    localStorage.setItem(TOKEN_KEY, access)
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  },
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    Accept: 'application/json',
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (tokens.access) headers.Authorization = `Bearer ${tokens.access}`

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (response.status === 401 && tokens.refresh) {
    // Try once to refresh the access token, then retry the original request.
    const refreshed = await tryRefresh()
    if (refreshed) {
      headers.Authorization = `Bearer ${tokens.access}`
      const retry = await fetch(`${API_BASE}${path}`, { ...options, headers })
      if (!retry.ok) throw new ApiError(retry.status, await errorDetail(retry))
      return retry.json()
    }
  }

  if (!response.ok) throw new ApiError(response.status, await errorDetail(response))
  if (response.status === 204) return undefined as T
  return response.json()
}

async function errorDetail(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
    const firstError = Object.values(body).flat()[0]
    if (typeof firstError === 'string') return firstError
  } catch {
    /* body was not JSON */
  }
  return `Request failed with HTTP ${response.status}`
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
  }
}

async function tryRefresh(): Promise<boolean> {
  if (!tokens.refresh) return false
  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokens.refresh }),
    })
    if (!response.ok) return false
    const data = await response.json()
    tokens.save(data.access)
    return true
  } catch {
    return false
  }
}

// -- endpoints ------------------------------------------------------------

export const api = {
  health: () => request<{ status: string; service: string }>('/api/v1/health/'),

  restaurants: (params: { search?: string; veg?: boolean; open?: boolean; sort?: string } = {}) => {
    const query = new URLSearchParams()
    if (params.search) query.set('search', params.search)
    if (params.veg) query.set('veg', '1')
    if (params.open) query.set('open', '1')
    if (params.sort) query.set('sort', params.sort)
    const qs = query.toString()
    return request<{ count: number; results: Restaurant[] }>(
      `/api/v1/restaurants/${qs ? `?${qs}` : ''}`,
    )
  },

  restaurant: (id: number | string) => request<RestaurantDetail>(`/api/v1/restaurants/${id}/`),

  cuisines: () => request<{ count: number; results: string[] }>('/api/v1/restaurants/cuisines/'),

  register: (payload: { email: string; name: string; phone?: string; password: string }) =>
    request<{ user: User; access: string; refresh: string }>('/api/v1/auth/register/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  login: (email: string, password: string) =>
    request<{ access: string; refresh: string }>('/api/v1/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  logout: () =>
    request<void>('/api/v1/auth/logout/', {
      method: 'POST',
      body: JSON.stringify({ refresh: tokens.refresh }),
    }),

  me: () => request<User>('/api/v1/auth/me/'),

  checkout: (payload: {
    restaurant_id: number
    items: Array<{ item_id: number; quantity: number }>
    delivery: { name: string; phone: string; address: string }
  }) =>
    request<CheckoutResponse>('/api/v1/orders/checkout/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  verifyPayment: (payload: {
    order_id: number
    razorpay_order_id?: string
    razorpay_payment_id?: string
    razorpay_signature?: string
  }) =>
    request<Order>('/api/v1/orders/verify-payment/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  myOrders: () => request<{ count: number; results: Order[] }>('/api/v1/orders/'),

  order: (id: number | string) => request<Order>(`/api/v1/orders/${id}/`),

  advanceOrder: (id: number | string) =>
    request<Order>(`/api/v1/orders/${id}/advance/`, { method: 'POST' }),

  cancelOrder: (id: number | string) =>
    request<Order>(`/api/v1/orders/${id}/cancel/`, { method: 'POST' }),
}

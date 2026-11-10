/** Razorpay Checkout global, injected by https://checkout.razorpay.com/v1/checkout.js */
declare global {
  interface Window {
    Razorpay?: new (options: RazorpayOptions) => { open: () => void }
  }
}

export type RazorpayOptions = {
  key: string
  order_id?: string
  amount?: number
  currency?: string
  name?: string
  description?: string
  prefill?: { name?: string; contact?: string; email?: string }
  theme?: { color?: string }
  handler?: (response: {
    razorpay_order_id: string
    razorpay_payment_id: string
    razorpay_signature: string
  }) => void
  modal?: { ondismiss?: () => void }
}

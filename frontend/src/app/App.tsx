import { Navigate, Route, HashRouter as Router, Routes } from 'react-router-dom'

import { Navbar } from '../components/Navbar'
import { AuthProvider } from '../context/AuthContext'
import { CartProvider } from '../context/CartContext'
import { CheckoutPage } from '../pages/CheckoutPage'
import { HomePage } from '../pages/HomePage'
import { LoginPage } from '../pages/LoginPage'
import { OrderDetailPage, OrderSuccessPage } from '../pages/OrderDetailPage'
import { OrdersPage } from '../pages/OrdersPage'
import { RegisterPage } from '../pages/RegisterPage'
import { RestaurantPage } from '../pages/RestaurantPage'

export default function App() {
  return (
    <AuthProvider>
      <CartProvider>
        {/* HashRouter works identically on Firebase Hosting, Render and the Android APK. */}
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/restaurant/:id" element={<RestaurantPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/order/:id" element={<OrderDetailPage />} />
            <Route path="/order/:id/success" element={<OrderSuccessPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <footer className="footer">
            <span>🍜 FoodFlow — Swiggy-style food ordering demo</span>
            <span>Django REST · Razorpay · React</span>
          </footer>
        </Router>
      </CartProvider>
    </AuthProvider>
  )
}

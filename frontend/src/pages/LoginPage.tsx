import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../context/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const redirectTo = (location.state as { from?: string } | null)?.from ?? '/'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await login(email.trim(), password)
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page page--narrow">
      <div className="auth-card">
        <h1 className="auth-card__title">Welcome back 🍜</h1>
        <p className="auth-card__subtitle">Log in to order food</p>

        <form onSubmit={onSubmit} className="form">
          <label className="form__label">
            Email
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
          </label>

          <label className="form__label">
            Password
            <input
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
            />
          </label>

          {error && <p className="form__error">{error}</p>}

          <button type="submit" className="btn btn--primary btn--full" disabled={busy}>
            {busy ? 'Logging in…' : 'Log in'}
          </button>
        </form>

        <p className="auth-card__switch">
          New to Foodiebay? <Link to="/register">Create an account</Link>
        </p>

        <div className="auth-card__demo">
          <p>Demo account: <code>demo@Foodiebay.app</code> / <code>demo1234</code></p>
        </div>
      </div>
    </div>
  )
}

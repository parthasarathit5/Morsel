import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import { api, tokens } from '../api/client'
import type { User } from '../types'

type AuthState =
  | { status: 'loading' }
  | { status: 'anonymous' }
  | { status: 'authenticated'; user: User }

type AuthContextValue = {
  state: AuthState
  login: (email: string, password: string) => Promise<void>
  register: (payload: { email: string; name: string; phone?: string; password: string }) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })

  useEffect(() => {
    if (!tokens.access) {
      setState({ status: 'anonymous' })
      return
    }
    api
      .me()
      .then((user) => setState({ status: 'authenticated', user }))
      .catch(() => {
        tokens.clear()
        setState({ status: 'anonymous' })
      })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.login(email, password)
    tokens.save(data.access, data.refresh)
    const user = await api.me()
    setState({ status: 'authenticated', user })
  }, [])

  const register = useCallback(async (payload: { email: string; name: string; phone?: string; password: string }) => {
    const data = await api.register(payload)
    tokens.save(data.access, data.refresh)
    setState({ status: 'authenticated', user: data.user })
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.logout()
    } catch {
      /* token may already be invalid — ignore */
    }
    tokens.clear()
    setState({ status: 'anonymous' })
  }, [])

  const value = useMemo(
    () => ({ state, login, register, logout }),
    [state, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>')
  return context
}

import React, { createContext, useContext, useEffect, useState } from 'react'
import { api, setToken as setApiToken } from '../api/client.js'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(() => localStorage.getItem('xeno_token') || '')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!token)

  useEffect(() => {
    setApiToken(token)
    if (!token) { setUser(null); setLoading(false); return }
    let cancelled = false
    api.get('/api/v1/auth/me/')
      .then((u) => { if (!cancelled) setUser(u) })
      .catch(() => { if (!cancelled) { setTokenState(''); localStorage.removeItem('xeno_token') } })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [token])

  async function login({ username, password }) {
    const res = await api.post('/api/v1/auth/login/', { username, password })
    localStorage.setItem('xeno_token', res.token)
    setTokenState(res.token)
    setUser(res.user)
  }

  async function register(payload) {
    const res = await api.post('/api/v1/auth/register/', payload)
    localStorage.setItem('xeno_token', res.token)
    setTokenState(res.token)
    setUser(res.user)
  }

  async function logout() {
    try { await api.post('/api/v1/auth/logout/', {}) } catch {}
    localStorage.removeItem('xeno_token')
    setTokenState('')
    setUser(null)
  }

  return (
    <Ctx.Provider value={{ token, user, loading, login, register, logout }}>
      {children}
    </Ctx.Provider>
  )
}

export const useAuth = () => useContext(Ctx)

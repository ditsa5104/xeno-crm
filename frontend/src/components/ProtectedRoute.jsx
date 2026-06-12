import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext.jsx'

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()
  const loc = useLocation()
  if (loading) {
    return (
      <div className="min-h-screen grid place-items-center bg-slate-50">
        <div className="animate-pulse text-slate-400 text-sm">Loading…</div>
      </div>
    )
  }
  if (!token) return <Navigate to="/login" replace state={{ from: loc.pathname }} />
  return children
}

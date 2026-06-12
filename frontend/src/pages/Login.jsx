import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Sparkles, Loader2, Mail, Lock } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'

export default function Login() {
  const nav = useNavigate()
  const loc = useLocation()
  const { login } = useAuth()
  const [form, setForm] = useState({ username: '', password: '' })
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setErr('')
    try {
      await login(form)
      nav(loc.state?.from || '/', { replace: true })
    } catch (e) {
      setErr(e.body?.non_field_errors?.[0] || e.body?.detail || 'Login failed')
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-slate-50">
      <div className="hidden lg:flex flex-col justify-between p-12 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 text-white">
        <div className="flex items-center gap-2 text-xl font-semibold">
          <Sparkles className="w-6 h-6" /> Xeno
        </div>
        <div>
          <h1 className="text-4xl font-bold leading-tight">The AI-native CRM for consumer brands.</h1>
          <p className="mt-4 text-white/80 max-w-md">
            Segment your customers in plain English. Draft personalised campaigns with an AI copilot. Track delivery and revenue in real time.
          </p>
          <div className="mt-8 grid grid-cols-3 gap-4 max-w-md">
            <Stat n="9" l="AI tools" />
            <Stat n="5" l="Channels" />
            <Stat n="∞" l="Possibilities" />
          </div>
        </div>
        <div className="text-xs text-white/60">© Xeno · Built for marketers who move fast.</div>
      </div>

      <div className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm space-y-5">
          <div className="lg:hidden flex items-center gap-2 text-2xl font-bold text-slate-900">
            <Sparkles className="w-6 h-6 text-indigo-600" /> Xeno
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Welcome back</h2>
            <p className="text-sm text-slate-500 mt-1">Sign in to your workspace.</p>
          </div>

          {err && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">{err}</div>}

          <Field icon={<Mail className="w-4 h-4" />} label="Username or email">
            <input
              autoFocus
              className="w-full bg-transparent outline-none text-sm"
              placeholder="you@example.com"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </Field>
          <Field icon={<Lock className="w-4 h-4" />} label="Password">
            <input
              type="password"
              className="w-full bg-transparent outline-none text-sm"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </Field>

          <button
            disabled={busy}
            className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 text-white text-sm font-medium py-2.5 hover:bg-slate-800 disabled:opacity-60"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            Sign in
          </button>

          <div className="text-sm text-slate-500 text-center">
            Don't have an account?{' '}
            <Link to="/register" className="text-indigo-600 font-medium hover:underline">Create one</Link>
          </div>
        </form>
      </div>
    </div>
  )
}

function Field({ icon, label, children }) {
  return (
    <label className="block">
      <span className="text-xs font-medium text-slate-600 mb-1 block">{label}</span>
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 bg-white focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100 transition">
        <span className="text-slate-400">{icon}</span>
        {children}
      </div>
    </label>
  )
}

function Stat({ n, l }) {
  return (
    <div>
      <div className="text-3xl font-bold">{n}</div>
      <div className="text-xs text-white/70">{l}</div>
    </div>
  )
}

import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Loader2, Mail, Lock } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'
import { LogoMark } from '../components/Logo.jsx'

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
      <div className="relative hidden lg:flex flex-col justify-between p-14 bg-[#0f1216] text-white overflow-hidden">
        {/* Restrained editorial backdrop: faint hairline grid, no gradient wash. */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '46px 46px' }}
        />
        <div className="absolute left-14 top-0 bottom-0 w-px bg-white/[0.06]" />

        <div className="relative flex items-center gap-2.5 text-lg font-semibold">
          <LogoMark className="w-9 h-9" /> Plume
        </div>

        <div className="relative max-w-md">
          <div className="h-px w-10 bg-emerald-400/80 mb-6" />
          <h1 className="text-[2.6rem] leading-[1.08] font-semibold tracking-tight">
            Reach the right shopper,<br />at the right moment.
          </h1>
          <p className="mt-5 text-[15px] leading-relaxed text-slate-400">
            Plume turns your customer and order data into segments, personalised
            messages, and multi-channel campaigns — with delivery and revenue
            tracked end to end.
          </p>
          <ul className="mt-8 space-y-3 text-sm text-slate-300">
            <li className="flex items-start gap-3"><span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" /> Segment shoppers by behaviour and value</li>
            <li className="flex items-start gap-3"><span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" /> Draft and send across WhatsApp, SMS, Email & RCS</li>
            <li className="flex items-start gap-3"><span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" /> Watch delivery and conversions in real time</li>
          </ul>
        </div>

        <div className="relative text-xs text-slate-500">© Plume · Built for marketers who move fast.</div>
      </div>

      <div className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm space-y-5">
          <div className="lg:hidden flex items-center gap-2 text-2xl font-bold text-slate-900">
            <LogoMark className="w-9 h-9" /> Plume
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Welcome back</h2>
            <p className="text-sm text-slate-500 mt-1">Sign in to your workspace.</p>
          </div>

          {err && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">{err}</div>}

          <div className="rounded-xl border border-indigo-200 bg-indigo-50/70 px-3.5 py-3 text-xs text-indigo-900">
            <span className="font-semibold">👋 Reviewer from Xeno?</span> Use the temp credentials below to see the CRM in action with mock data — username <code className="font-mono font-semibold">tempuser_check</code>, password <code className="font-mono font-semibold">TempPass#2026</code>.
          </div>

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

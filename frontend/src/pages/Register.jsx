import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Loader2, User, Mail, Lock, AtSign } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext.jsx'
import { LogoMark } from '../components/Logo.jsx'

export default function Register() {
  const nav = useNavigate()
  const { register } = useAuth()
  const [form, setForm] = useState({ name: '', username: '', email: '', password: '' })
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  async function submit(e) {
    e.preventDefault()
    setBusy(true); setErr('')
    try {
      await register(form)
      nav('/', { replace: true })
    } catch (e) {
      const body = e.body || {}
      const msg = body.username?.[0] || body.email?.[0] || body.password?.[0] || body.detail || 'Registration failed'
      setErr(msg)
    } finally { setBusy(false) }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-slate-50">
      <div className="relative hidden lg:flex flex-col justify-between p-14 bg-[#0f1216] text-white overflow-hidden">
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
            From customer data<br />to campaign, in minutes.
          </h1>
          <p className="mt-5 text-[15px] leading-relaxed text-slate-400">
            Describe who you want to reach in plain language. Plume builds the
            segment, drafts the message, picks the channel, and tracks every
            send through to conversion.
          </p>
          <ul className="mt-8 space-y-3 text-sm text-slate-300">
            <li className="flex items-start gap-3"><span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" /> Plain-English customer segmentation</li>
            <li className="flex items-start gap-3"><span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" /> Multi-channel dispatch with smart retries</li>
            <li className="flex items-start gap-3"><span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" /> Real-time delivery and conversion tracking</li>
          </ul>
        </div>

        <div className="relative text-xs text-slate-500">© Plume · Privacy first. Always.</div>
      </div>

      <div className="flex items-center justify-center p-6">
        <form onSubmit={submit} className="w-full max-w-sm space-y-5">
          <div className="lg:hidden flex items-center gap-2 text-2xl font-bold text-slate-900">
            <LogoMark className="w-9 h-9" /> Plume
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Create your account</h2>
            <p className="text-sm text-slate-500 mt-1">Free to get started — no credit card.</p>
          </div>

          {err && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">{err}</div>}

          <div className="rounded-xl border border-indigo-200 bg-indigo-50/70 px-3.5 py-3 text-xs text-indigo-900">
            <span className="font-semibold">👋 Reviewer from Xeno?</span> No need to sign up — <Link to="/login" className="font-semibold underline">sign in</Link> with the temp credentials (<code className="font-mono font-semibold">tempuser_check</code> / <code className="font-mono font-semibold">TempPass#2026</code>) to see the CRM in action with mock data.
          </div>

          <Field icon={<User className="w-4 h-4" />} label="Full name">
            <input
              autoFocus
              className="w-full bg-transparent outline-none text-sm"
              placeholder="Alex Patel"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </Field>
          <Field icon={<AtSign className="w-4 h-4" />} label="Username">
            <input
              className="w-full bg-transparent outline-none text-sm"
              placeholder="alexp"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required minLength={3}
            />
          </Field>
          <Field icon={<Mail className="w-4 h-4" />} label="Email">
            <input
              type="email"
              className="w-full bg-transparent outline-none text-sm"
              placeholder="alex@brand.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </Field>
          <Field icon={<Lock className="w-4 h-4" />} label="Password">
            <input
              type="password"
              className="w-full bg-transparent outline-none text-sm"
              placeholder="At least 6 characters"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required minLength={6}
            />
          </Field>

          <button
            disabled={busy}
            className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 text-white text-sm font-medium py-2.5 hover:bg-slate-800 disabled:opacity-60"
          >
            {busy && <Loader2 className="w-4 h-4 animate-spin" />}
            Create account
          </button>

          <div className="text-sm text-slate-500 text-center">
            Already have an account?{' '}
            <Link to="/login" className="text-indigo-600 font-medium hover:underline">Sign in</Link>
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

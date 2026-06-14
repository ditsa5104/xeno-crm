import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, MessageSquare, Mail, Smartphone, Clock, Send } from 'lucide-react'
import { api } from '../api/client.js'
import PageHeader from '../components/PageHeader.jsx'
import MessagePreview from '../components/MessagePreview.jsx'

const CHANNELS = [
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageSquare },
  { id: 'sms', label: 'SMS', icon: Smartphone },
  { id: 'email', label: 'Email', icon: Mail },
  { id: 'rcs', label: 'RCS', icon: MessageSquare },
  { id: 'auto', label: 'Auto', icon: MessageSquare },
]

export default function CampaignBuilder() {
  const nav = useNavigate()
  const segs = useQuery({ queryKey: ['segs'], queryFn: () => api.get('/api/v1/segments/') })
  const [form, setForm] = useState({
    name: '',
    segment: '',
    channel: 'whatsapp',
    message_template: 'Hi {{name}}, exclusive offer just for you in {{city}}!',
  })
  const [scheduledAt, setScheduledAt] = useState('')
  const [err, setErr] = useState('')

  // Create the draft, then either launch now or schedule for later based on the
  // chosen send time.
  const submit = useMutation({
    mutationFn: async (mode) => {
      const campaign = await api.post('/api/v1/campaigns/', form)
      if (mode === 'schedule') {
        // Browser datetime-local has no timezone; send as local ISO and let the
        // backend interpret it in the server timezone.
        await api.post(`/api/v1/campaigns/${campaign.id}/schedule/`, {
          scheduled_at: new Date(scheduledAt).toISOString(),
        })
      } else if (mode === 'launch') {
        await api.post(`/api/v1/campaigns/${campaign.id}/launch/`, {})
      }
      return campaign
    },
    onSuccess: (c) => nav(`/campaigns/${c.id}`),
    onError: (e) => setErr(e.body?.error || e.message || 'Something went wrong'),
  })

  // Minimum selectable time = 5 minutes from now, formatted for datetime-local.
  const minDateTime = (() => {
    const d = new Date(Date.now() + 5 * 60 * 1000)
    d.setSeconds(0, 0)
    const pad = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
  })()

  const create = submit  // alias kept for existing button handlers

  const previewBody = form.message_template
    .replace(/\{\{name\}\}/g, 'Alex')
    .replace(/\{\{city\}\}/g, 'Mumbai')
    .replace(/\{\{first_name\}\}/g, 'Alex')
    .replace(/\{\{last_order_amount\}\}/g, '2,499')

  return (
    <div className="space-y-6">
      <Link to="/campaigns" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900">
        <ArrowLeft className="w-4 h-4" /> Back to campaigns
      </Link>

      <PageHeader title="New campaign" subtitle="Draft, launch now, or schedule for a future date & time." />

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card p-5 space-y-4">
          <Field label="Campaign name">
            <input className="input" placeholder="e.g. Spring Drop VIP" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </Field>
          <Field label="Audience">
            <select className="input" value={form.segment} onChange={(e) => setForm({ ...form, segment: e.target.value })}>
              <option value="">— pick a segment —</option>
              {(segs.data?.results || []).map((s) => (
                <option key={s.id} value={s.id}>{s.name} ({s.customer_count})</option>
              ))}
            </select>
          </Field>
          <Field label="Channel">
            <div className="grid grid-cols-5 gap-2">
              {CHANNELS.map((c) => {
                const Icon = c.icon
                const active = form.channel === c.id
                return (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setForm({ ...form, channel: c.id })}
                    className={`flex flex-col items-center gap-1 px-2 py-2.5 rounded-lg border text-xs font-medium transition ${
                      active ? 'border-emerald-500 bg-emerald-50 text-emerald-700 ring-2 ring-emerald-100' : 'border-slate-200 hover:bg-slate-50 text-slate-600'
                    }`}
                  >
                    <Icon className="w-4 h-4" /> {c.label}
                  </button>
                )
              })}
            </div>
          </Field>
          <Field label="Message" hint="Use merge tags like {{name}}, {{city}}, {{last_order_amount}}.">
            <textarea
              rows={6}
              className="input font-mono text-xs"
              value={form.message_template}
              onChange={(e) => setForm({ ...form, message_template: e.target.value })}
            />
          </Field>
          <Field label="Schedule send" hint="Leave empty to save as a draft you can launch manually. Set a future date & time to schedule automatic sending.">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400 shrink-0" />
              <input
                type="datetime-local"
                className="input"
                min={minDateTime}
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
              />
              {scheduledAt && (
                <button type="button" onClick={() => setScheduledAt('')} className="text-xs text-slate-400 hover:text-slate-700 shrink-0">
                  Clear
                </button>
              )}
            </div>
          </Field>

          {err && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">{err}</div>}

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => { setErr(''); submit.mutate('draft') }}
              disabled={!form.name || !form.segment || submit.isPending}
              className="btn-secondary"
            >
              {submit.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Save draft
            </button>
            {scheduledAt ? (
              <button
                onClick={() => { setErr(''); submit.mutate('schedule') }}
                disabled={!form.name || !form.segment || submit.isPending}
                className="btn-primary"
              >
                {submit.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Clock className="w-4 h-4" />}
                Schedule send
              </button>
            ) : (
              <button
                onClick={() => { setErr(''); submit.mutate('launch') }}
                disabled={!form.name || !form.segment || submit.isPending}
                className="btn-gradient"
              >
                {submit.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                Launch now
              </button>
            )}
            <Link to="/campaigns" className="btn-ghost">Cancel</Link>
          </div>
        </div>

        <div>
          <div className="text-xs uppercase tracking-wide text-slate-500 mb-2 font-medium">Live preview</div>
          <MessagePreview channel={form.channel} body={previewBody} />
        </div>
      </div>
    </div>
  )
}

function Field({ label, hint, children }) {
  return (
    <label className="block">
      <div className="text-xs font-medium text-slate-700 mb-1.5">{label}</div>
      {children}
      {hint && <div className="text-xs text-slate-400 mt-1">{hint}</div>}
    </label>
  )
}

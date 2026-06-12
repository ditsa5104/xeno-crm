import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Loader2, MessageSquare, Mail, Smartphone } from 'lucide-react'
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
  const create = useMutation({
    mutationFn: () => api.post('/api/v1/campaigns/', form),
    onSuccess: (c) => nav(`/campaigns/${c.id}`),
  })

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

      <PageHeader title="New campaign" subtitle="Draft your campaign — launch when ready." />

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
                      active ? 'border-indigo-500 bg-indigo-50 text-indigo-700 ring-2 ring-indigo-100' : 'border-slate-200 hover:bg-slate-50 text-slate-600'
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
          <div className="flex gap-2">
            <button onClick={() => create.mutate()} disabled={!form.name || !form.segment || create.isPending} className="btn-primary">
              {create.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Save draft
            </button>
            <Link to="/campaigns" className="btn-secondary">Cancel</Link>
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

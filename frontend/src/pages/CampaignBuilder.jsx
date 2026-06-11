import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

export default function CampaignBuilder() {
  const nav = useNavigate()
  const segs = useQuery({ queryKey: ['segs'], queryFn: () => api.get('/api/v1/segments/') })
  const [form, setForm] = useState({ name: '', segment: '', channel: 'whatsapp', message_template: 'Hi {{name}}, exclusive offer just for you in {{city}}!' })
  const create = useMutation({
    mutationFn: () => api.post('/api/v1/campaigns/', form),
    onSuccess: (c) => nav(`/campaigns/${c.id}`),
  })
  return (
    <div className="space-y-3 max-w-2xl">
      <h1 className="text-2xl font-bold">New campaign</h1>
      <input className="w-full border rounded px-2 py-1" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
      <select className="w-full border rounded px-2 py-1" value={form.segment} onChange={(e) => setForm({ ...form, segment: e.target.value })}>
        <option value="">— pick a segment —</option>
        {(segs.data?.results || []).map((s) => <option key={s.id} value={s.id}>{s.name} ({s.customer_count})</option>)}
      </select>
      <select className="w-full border rounded px-2 py-1" value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}>
        {['whatsapp', 'sms', 'email', 'rcs', 'auto'].map((c) => <option key={c} value={c}>{c}</option>)}
      </select>
      <textarea
        className="w-full border rounded px-2 py-1 h-32"
        value={form.message_template}
        onChange={(e) => setForm({ ...form, message_template: e.target.value })}
      />
      <p className="text-xs text-gray-500">Use merge tags like {'{{name}}'}, {'{{city}}'}, {'{{last_order_amount}}'}.</p>
      <button onClick={() => create.mutate()} disabled={!form.name || !form.segment} className="bg-indigo-600 text-white rounded px-4 py-2 disabled:opacity-50">Save draft</button>
    </div>
  )
}

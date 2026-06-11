import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client.js'
import FunnelChart from '../components/FunnelChart.jsx'
import MessagePreview from '../components/MessagePreview.jsx'

export default function CampaignDetail() {
  const { id } = useParams()
  const qc = useQueryClient()
  const camp = useQuery({ queryKey: ['camp', id], queryFn: () => api.get(`/api/v1/campaigns/${id}/`), refetchInterval: 5000 })
  const launch = useMutation({
    mutationFn: () => api.post(`/api/v1/campaigns/${id}/launch/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['camp', id] }),
  })
  const preflight = useMutation({ mutationFn: () => api.post(`/api/v1/campaigns/${id}/preflight/`) })

  if (camp.isLoading) return <div>Loading…</div>
  const c = camp.data
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">{c.name}</h1>
          <div className="text-sm text-gray-500">Status: {c.status} · {c.channel}</div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => preflight.mutate()} className="border rounded px-3 py-1 text-sm">Preflight</button>
          <button onClick={() => launch.mutate()} className="bg-indigo-600 text-white rounded px-3 py-1 text-sm">Launch</button>
        </div>
      </div>

      <MessagePreview channel={c.channel} body={c.message_template} />

      {preflight.data && (
        <div className="bg-amber-50 border border-amber-200 rounded p-3 text-sm">
          <div>Audience: {preflight.data.audience_size} · est. delivery {Math.round(preflight.data.estimated_delivery_rate * 100)}%</div>
          {preflight.data.message_previews?.map((p, i) => <div key={i} className="text-xs text-gray-700 mt-1">→ {p}</div>)}
        </div>
      )}

      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-2">Funnel</h2>
        <FunnelChart stats={{
          total: c.stat_total, sent: c.stat_sent, delivered: c.stat_delivered,
          opened: c.stat_opened, clicked: c.stat_clicked, converted: c.stat_converted,
        }} />
      </div>
    </div>
  )
}

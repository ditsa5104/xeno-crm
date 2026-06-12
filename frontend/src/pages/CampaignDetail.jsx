import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Play, Pause, ListChecks, Loader2, AlertCircle } from 'lucide-react'
import { api } from '../api/client.js'
import FunnelChart from '../components/FunnelChart.jsx'
import MessagePreview from '../components/MessagePreview.jsx'
import { CardSkeleton } from '../components/Skeleton.jsx'

const STATUS_STYLE = {
  draft: 'bg-slate-100 text-slate-700 ring-slate-200',
  scheduled: 'bg-blue-50 text-blue-700 ring-blue-200',
  running: 'bg-amber-50 text-amber-700 ring-amber-200',
  paused: 'bg-yellow-50 text-yellow-700 ring-yellow-200',
  completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  failed: 'bg-red-50 text-red-700 ring-red-200',
}

function pct(num, den) { return den ? `${(num / den * 100).toFixed(1)}%` : '—' }

export default function CampaignDetail() {
  const { id } = useParams()
  const qc = useQueryClient()
  const camp = useQuery({
    queryKey: ['camp', id],
    queryFn: () => api.get(`/api/v1/campaigns/${id}/`),
    refetchInterval: 5000,
  })
  const launch = useMutation({
    mutationFn: () => api.post(`/api/v1/campaigns/${id}/launch/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['camp', id] }),
  })
  const pause = useMutation({
    mutationFn: () => api.post(`/api/v1/campaigns/${id}/pause/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['camp', id] }),
  })
  const preflight = useMutation({ mutationFn: () => api.post(`/api/v1/campaigns/${id}/preflight/`) })

  if (camp.isLoading) return <CardSkeleton height="h-64" />
  const c = camp.data

  return (
    <div className="space-y-6">
      <Link to="/campaigns" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900">
        <ArrowLeft className="w-4 h-4" /> Back to campaigns
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold tracking-tight">{c.name}</h1>
            <span className={`chip ring-1 ${STATUS_STYLE[c.status] || STATUS_STYLE.draft}`}>{c.status}</span>
          </div>
          <div className="text-sm text-slate-500 mt-1 capitalize">{c.channel} · {c.segment_name || 'Segment'}</div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => preflight.mutate()} disabled={preflight.isPending} className="btn-secondary">
            {preflight.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <ListChecks className="w-4 h-4" />}
            Preflight
          </button>
          {c.status === 'running' ? (
            <button onClick={() => pause.mutate()} className="btn-secondary"><Pause className="w-4 h-4" /> Pause</button>
          ) : (
            <button
              onClick={() => launch.mutate()}
              disabled={launch.isPending || c.status === 'completed'}
              className="btn-gradient"
            >
              {launch.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Launch
            </button>
          )}
        </div>
      </div>

      {preflight.data && (
        <div className="card p-4 border-amber-200 bg-amber-50/50">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1 text-sm">
              <div className="font-medium text-amber-900">Preflight check</div>
              <div className="text-amber-800 mt-1">
                Audience: <strong>{preflight.data.audience_size}</strong> · estimated delivery <strong>{Math.round(preflight.data.estimated_delivery_rate * 100)}%</strong>
              </div>
              {preflight.data.message_previews?.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  <div className="text-xs uppercase tracking-wide text-amber-700">Sample messages</div>
                  {preflight.data.message_previews.map((p, i) => (
                    <div key={i} className="text-xs text-amber-900 bg-white/60 rounded px-2 py-1.5 border border-amber-200">{p}</div>
                  ))}
                </div>
              )}
              {preflight.data.warnings?.length > 0 && (
                <div className="mt-2 text-xs text-red-700">⚠ {preflight.data.warnings.join('; ')}</div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-4">
        <Stat label="Audience" value={c.stat_total} />
        <Stat label="Delivery rate" value={pct(c.stat_delivered, c.stat_total)} />
        <Stat label="Click rate" value={pct(c.stat_clicked, c.stat_delivered)} />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card p-5">
          <h2 className="font-semibold mb-3">Funnel</h2>
          <FunnelChart stats={{
            total: c.stat_total, sent: c.stat_sent, delivered: c.stat_delivered,
            opened: c.stat_opened, clicked: c.stat_clicked, converted: c.stat_converted,
          }} />
        </div>
        <div>
          <div className="text-xs uppercase tracking-wide text-slate-500 mb-2 font-medium">Message</div>
          <MessagePreview channel={c.channel} body={c.message_template} />
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="card p-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="text-2xl font-bold mt-1 text-slate-900">{value}</div>
    </div>
  )
}

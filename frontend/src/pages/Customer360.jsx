import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Mail, Phone, MapPin, Radio, AlertTriangle, Wallet } from 'lucide-react'
import { api } from '../api/client.js'
import RFMBadge from '../components/RFMBadge.jsx'
import CustomerTimeline from '../components/CustomerTimeline.jsx'
import { CardSkeleton } from '../components/Skeleton.jsx'

export default function Customer360() {
  const { id } = useParams()
  const cust = useQuery({ queryKey: ['cust', id], queryFn: () => api.get(`/api/v1/customers/${id}/`) })
  const tl = useQuery({ queryKey: ['tl', id], queryFn: () => api.get(`/api/v1/customers/${id}/timeline/`) })

  if (cust.isLoading) return <CardSkeleton height="h-48" />
  const c = cust.data
  const initials = (c.name || '?').split(' ').map((s) => s[0]).slice(0, 2).join('').toUpperCase()

  return (
    <div className="space-y-6">
      <Link to="/customers" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900">
        <ArrowLeft className="w-4 h-4" /> Back to customers
      </Link>

      <div className="card p-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 grid place-items-center text-white text-xl font-bold shadow">
            {initials}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-slate-900">{c.name}</h1>
              <RFMBadge tier={c.rfm_tier} />
            </div>
            <div className="flex gap-4 mt-1 text-sm text-slate-500 flex-wrap">
              {c.email && <span className="inline-flex items-center gap-1"><Mail className="w-3.5 h-3.5" />{c.email}</span>}
              {c.phone && <span className="inline-flex items-center gap-1"><Phone className="w-3.5 h-3.5" />{c.phone}</span>}
              {c.city && <span className="inline-flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{c.city}</span>}
              <span className="inline-flex items-center gap-1"><Radio className="w-3.5 h-3.5" />{c.channel_preference}</span>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <Metric icon={Wallet} label="Total spend" value={`₹${Number(c.total_spend).toLocaleString('en-IN')}`} />
          <Metric label="Total orders" value={c.total_orders} />
          <Metric label="Last order" value={c.last_order_at ? new Date(c.last_order_at).toLocaleDateString() : '—'} />
          <Metric icon={AlertTriangle} label="Churn risk" value={`${(c.churn_risk_score * 100).toFixed(0)}%`} accent={c.churn_risk_score > 0.6 ? 'red' : 'default'} />
        </div>
      </div>

      <div className="card p-6">
        <h2 className="font-semibold mb-4">Activity timeline</h2>
        {tl.isLoading ? <div className="skeleton h-32 w-full" /> : <CustomerTimeline orders={tl.data.orders} communications={tl.data.communications} />}
      </div>
    </div>
  )
}

function Metric({ icon: Icon, label, value, accent = 'default' }) {
  const cls = accent === 'red' ? 'text-red-600' : 'text-slate-900'
  return (
    <div className="rounded-lg border border-slate-200 p-3 bg-slate-50/50">
      <div className="flex items-center gap-1.5 text-xs text-slate-500 uppercase tracking-wide">
        {Icon && <Icon className="w-3 h-3" />}
        {label}
      </div>
      <div className={`text-xl font-semibold mt-1 ${cls}`}>{value}</div>
    </div>
  )
}

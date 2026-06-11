import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client.js'
import RFMBadge from '../components/RFMBadge.jsx'
import CustomerTimeline from '../components/CustomerTimeline.jsx'

export default function Customer360() {
  const { id } = useParams()
  const cust = useQuery({ queryKey: ['cust', id], queryFn: () => api.get(`/api/v1/customers/${id}/`) })
  const tl = useQuery({ queryKey: ['tl', id], queryFn: () => api.get(`/api/v1/customers/${id}/timeline/`) })

  if (cust.isLoading) return <div>Loading…</div>
  const c = cust.data
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg border p-4">
        <h1 className="text-2xl font-bold">{c.name}</h1>
        <div className="text-sm text-gray-500">{c.email} • {c.phone}</div>
        <div className="mt-3 flex gap-2 flex-wrap">
          <RFMBadge tier={c.rfm_tier} />
          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">City: {c.city}</span>
          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">Channel: {c.channel_preference}</span>
          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">Churn risk: {(c.churn_risk_score * 100).toFixed(0)}%</span>
          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">LTV: ₹{c.ltv_estimate}</span>
        </div>
        <div className="mt-3 grid grid-cols-3 gap-3 text-sm">
          <div><div className="text-gray-400">Total spend</div><div>₹{c.total_spend}</div></div>
          <div><div className="text-gray-400">Total orders</div><div>{c.total_orders}</div></div>
          <div><div className="text-gray-400">Last order</div><div>{c.last_order_at ? new Date(c.last_order_at).toLocaleDateString() : '—'}</div></div>
        </div>
      </div>
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-3">Timeline</h2>
        {tl.isLoading ? <div>…</div> : <CustomerTimeline orders={tl.data.orders} communications={tl.data.communications} />}
      </div>
    </div>
  )
}

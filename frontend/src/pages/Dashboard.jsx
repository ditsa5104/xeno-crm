import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client.js'
import LiveEventFeed from '../components/LiveEventFeed.jsx'

function Stat({ label, value }) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="text-xs text-gray-500 uppercase">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
    </div>
  )
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/api/v1/analytics/dashboard/'),
  })
  if (isLoading) return <div>Loading…</div>
  if (error) return <div className="text-red-600">{error.message}</div>
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Stat label="Customers" value={data.total_customers} />
        <Stat label="Segments" value={data.active_segments} />
        <Stat label="Campaigns / month" value={data.campaigns_this_month} />
        <Stat label="Messages / month" value={data.messages_this_month} />
        <Stat label="Delivery rate" value={`${(data.overall_delivery_rate * 100).toFixed(1)}%`} />
      </div>
      <LiveEventFeed />
    </div>
  )
}

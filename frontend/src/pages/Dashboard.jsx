import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users, Layers, Megaphone, Send, TrendingUp } from 'lucide-react'
import { api } from '../api/client.js'
import LiveEventFeed from '../components/LiveEventFeed.jsx'
import PageHeader from '../components/PageHeader.jsx'
import StatCard from '../components/StatCard.jsx'
import { CardSkeleton } from '../components/Skeleton.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'

export default function Dashboard() {
  const { user } = useAuth()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/api/v1/analytics/dashboard/'),
  })

  const firstName = user?.name?.split(' ')[0] || user?.username

  return (
    <div>
      <PageHeader
        title={firstName ? `Welcome back, ${firstName} 👋` : 'Dashboard'}
        subtitle="Here's a snapshot of your CRM today."
      />

      {error && (
        <div className="card p-4 mb-6 border-red-200 bg-red-50 text-red-700 text-sm">{error.message}</div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {isLoading ? (
          Array.from({ length: 5 }).map((_, i) => <CardSkeleton key={i} height="h-28" />)
        ) : data && (
          <>
            <StatCard label="Customers" value={data.total_customers} icon={Users} accent="indigo" />
            <StatCard label="Segments" value={data.active_segments} icon={Layers} accent="purple" />
            <StatCard label="Campaigns / mo" value={data.campaigns_this_month} icon={Megaphone} accent="pink" />
            <StatCard label="Messages / mo" value={data.messages_this_month} icon={Send} accent="amber" />
            <StatCard label="Delivery rate" value={`${(data.overall_delivery_rate * 100).toFixed(1)}%`} icon={TrendingUp} accent="emerald" />
          </>
        )}
      </div>

      <div className="mt-6">
        <LiveEventFeed />
      </div>
    </div>
  )
}

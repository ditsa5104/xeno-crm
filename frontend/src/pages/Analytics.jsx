import React from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend,
  LineChart, Line, CartesianGrid,
} from 'recharts'
import { api } from '../api/client.js'
import PageHeader from '../components/PageHeader.jsx'
import { CardSkeleton } from '../components/Skeleton.jsx'

const TOOLTIP = { borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }

export default function Analytics() {
  const channels = useQuery({ queryKey: ['ch'], queryFn: () => api.get('/api/v1/analytics/channels/') })
  const cohorts = useQuery({ queryKey: ['co'], queryFn: () => api.get('/api/v1/analytics/cohorts/') })

  return (
    <div className="space-y-6">
      <PageHeader title="Analytics" subtitle="Channel performance and customer cohorts." />

      <div className="card p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">By channel</h2>
          <span className="text-xs text-slate-400">Delivered · Clicked · Failed</span>
        </div>
        {channels.isLoading ? <CardSkeleton height="h-72" /> : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={channels.data || []} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="channel" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={TOOLTIP} cursor={{ fill: '#f8fafc' }} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="delivered" fill="#10b981" radius={[6, 6, 0, 0]} />
              <Bar dataKey="clicked" fill="#0d9488" radius={[6, 6, 0, 0]} />
              <Bar dataKey="failed" fill="#ef4444" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Cohorts</h2>
          <span className="text-xs text-slate-400">Acquired customers and spend by month</span>
        </div>
        {cohorts.isLoading ? <CardSkeleton height="h-72" /> : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={cohorts.data || []} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(m) => m?.slice(0, 7)} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={TOOLTIP} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="customers" stroke="#0d9488" strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 5 }} />
              <Line type="monotone" dataKey="spend" stroke="#10b981" strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

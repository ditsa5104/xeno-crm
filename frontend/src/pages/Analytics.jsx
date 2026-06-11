import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, LineChart, Line } from 'recharts'
import { api } from '../api/client.js'

export default function Analytics() {
  const channels = useQuery({ queryKey: ['ch'], queryFn: () => api.get('/api/v1/analytics/channels/') })
  const cohorts = useQuery({ queryKey: ['co'], queryFn: () => api.get('/api/v1/analytics/cohorts/') })
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-2">By channel</h2>
        {channels.data && (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={channels.data}>
              <XAxis dataKey="channel" /><YAxis /><Tooltip />
              <Bar dataKey="delivered" fill="#10b981" />
              <Bar dataKey="clicked" fill="#6366f1" />
              <Bar dataKey="failed" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-2">Cohorts (acquisition month)</h2>
        {cohorts.data && (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={cohorts.data}>
              <XAxis dataKey="month" /><YAxis /><Tooltip />
              <Line type="monotone" dataKey="customers" stroke="#6366f1" />
              <Line type="monotone" dataKey="spend" stroke="#10b981" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

import React from 'react'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'

export default function FunnelChart({ stats }) {
  const data = [
    { stage: 'Total', count: stats.total },
    { stage: 'Sent', count: stats.sent },
    { stage: 'Delivered', count: stats.delivered },
    { stage: 'Opened', count: stats.opened },
    { stage: 'Clicked', count: stats.clicked },
    { stage: 'Converted', count: stats.converted },
  ]
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical">
        <XAxis type="number" />
        <YAxis dataKey="stage" type="category" width={80} />
        <Tooltip />
        <Bar dataKey="count" fill="#6366f1" />
      </BarChart>
    </ResponsiveContainer>
  )
}

import React from 'react'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts'

const COLORS = ['#064e3b', '#047857', '#059669', '#10b981', '#34d399', '#6ee7b7']

export default function FunnelChart({ stats }) {
  const data = [
    { stage: 'Audience', count: stats.total },
    { stage: 'Sent', count: stats.sent },
    { stage: 'Delivered', count: stats.delivered },
    { stage: 'Opened', count: stats.opened },
    { stage: 'Clicked', count: stats.clicked },
    { stage: 'Converted', count: stats.converted },
  ]
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} layout="vertical" margin={{ left: 12, right: 16, top: 4, bottom: 4 }}>
        <XAxis type="number" stroke="#94a3b8" fontSize={11} />
        <YAxis dataKey="stage" type="category" width={80} stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
        <Tooltip
          cursor={{ fill: '#f1f5f9' }}
          contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]}>
          {data.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

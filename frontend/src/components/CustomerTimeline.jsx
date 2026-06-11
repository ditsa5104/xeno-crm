import React from 'react'

export default function CustomerTimeline({ orders, communications }) {
  const items = [
    ...orders.map((o) => ({ kind: 'order', date: o.ordered_at, label: `Order ${o.order_number} — ₹${o.total_amount} (${o.status})` })),
    ...communications.map((c) => ({ kind: 'comm', date: c.queued_at, label: `${c.campaign_name} (${c.channel}) → ${c.status}` })),
  ].sort((a, b) => new Date(b.date) - new Date(a.date))
  return (
    <ol className="border-l border-gray-200 pl-4 space-y-3">
      {items.map((it, i) => (
        <li key={i} className="relative">
          <span className={`absolute -left-[9px] top-1.5 w-2.5 h-2.5 rounded-full ${
            it.kind === 'order' ? 'bg-emerald-500' : 'bg-indigo-500'
          }`} />
          <div className="text-xs text-gray-400">{new Date(it.date).toLocaleString()}</div>
          <div className="text-sm">{it.label}</div>
        </li>
      ))}
      {items.length === 0 && <li className="text-sm text-gray-400">No activity yet.</li>}
    </ol>
  )
}

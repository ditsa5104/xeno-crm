import React from 'react'
import { ShoppingBag, Send } from 'lucide-react'

export default function CustomerTimeline({ orders, communications }) {
  const items = [
    ...orders.map((o) => ({
      kind: 'order',
      date: o.ordered_at,
      title: `Order ${o.order_number}`,
      meta: `₹${Number(o.total_amount).toLocaleString('en-IN')} · ${o.status}`,
    })),
    ...communications.map((c) => ({
      kind: 'comm',
      date: c.queued_at,
      title: c.campaign_name,
      meta: `${c.channel} · ${c.status}`,
    })),
  ].sort((a, b) => new Date(b.date) - new Date(a.date))

  if (items.length === 0) {
    return <div className="text-sm text-slate-400 text-center py-6">No activity yet.</div>
  }

  return (
    <ol className="relative border-l-2 border-slate-100 pl-6 space-y-5 ml-2">
      {items.map((it, i) => {
        const Icon = it.kind === 'order' ? ShoppingBag : Send
        const color = it.kind === 'order' ? 'bg-emerald-500' : 'bg-teal-500'
        return (
          <li key={i} className="relative">
            <span className={`absolute -left-[34px] top-0 w-7 h-7 rounded-full ${color} grid place-items-center text-white shadow ring-4 ring-white`}>
              <Icon className="w-3.5 h-3.5" />
            </span>
            <div className="text-xs text-slate-400">{new Date(it.date).toLocaleString()}</div>
            <div className="text-sm font-medium text-slate-900">{it.title}</div>
            <div className="text-xs text-slate-500 capitalize">{it.meta}</div>
          </li>
        )
      })}
    </ol>
  )
}

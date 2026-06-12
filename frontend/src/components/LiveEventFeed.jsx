import React from 'react'
import { Activity, Wifi } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket.js'

const COLORS = {
  sent: 'bg-blue-50 text-blue-700 ring-1 ring-blue-200',
  delivered: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
  failed: 'bg-red-50 text-red-700 ring-1 ring-red-200',
  opened: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
  read: 'bg-purple-50 text-purple-700 ring-1 ring-purple-200',
  clicked: 'bg-pink-50 text-pink-700 ring-1 ring-pink-200',
}

export default function LiveEventFeed() {
  const { events } = useWebSocket()
  return (
    <div className="card overflow-hidden">
      <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-slate-400" />
          <div className="font-semibold text-sm">Live events</div>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-emerald-600">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          Connected
        </div>
      </div>
      <div className="p-3 max-h-80 overflow-y-auto">
        {events.length === 0 && (
          <div className="text-center py-8 text-xs text-slate-400 flex flex-col items-center gap-2">
            <Wifi className="w-5 h-5" />
            Waiting for events… launch a campaign to see live activity here.
          </div>
        )}
        <ul className="divide-y divide-slate-100">
          {events.map((e, i) => (
            <li key={i} className="flex items-center gap-3 py-2 text-xs">
              <span className={`chip ${COLORS[e.event_type] || 'bg-slate-100 text-slate-600'}`}>
                {e.event_type}
              </span>
              <span className="text-slate-500 capitalize">{e.channel}</span>
              <span className="font-mono text-slate-400 truncate">{e.log_id?.slice(0, 8)}</span>
              <span className="ml-auto text-slate-400">{e.timestamp?.slice(11, 19)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

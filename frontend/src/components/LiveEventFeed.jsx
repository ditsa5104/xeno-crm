import React from 'react'
import { useWebSocket } from '../hooks/useWebSocket.js'

const COLORS = {
  sent: 'bg-blue-100 text-blue-800',
  delivered: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  opened: 'bg-yellow-100 text-yellow-800',
  read: 'bg-purple-100 text-purple-800',
  clicked: 'bg-pink-100 text-pink-800',
}

export default function LiveEventFeed() {
  const { events } = useWebSocket()
  return (
    <div className="bg-white rounded-lg border p-3 h-72 overflow-y-auto">
      <div className="font-semibold mb-2 text-sm">Live events</div>
      {events.length === 0 && <div className="text-xs text-gray-400">Waiting for events…</div>}
      <ul className="space-y-1 text-xs">
        {events.map((e, i) => (
          <li key={i} className="flex items-center gap-2">
            <span className={`px-1.5 py-0.5 rounded ${COLORS[e.event_type] || 'bg-gray-100'}`}>
              {e.event_type}
            </span>
            <span className="text-gray-500">{e.channel}</span>
            <span className="text-gray-400 truncate">{e.log_id?.slice(0, 8)}</span>
            <span className="ml-auto text-gray-300">{e.timestamp?.slice(11, 19)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

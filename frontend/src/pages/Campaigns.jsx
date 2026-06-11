import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client.js'

const STATUS_COLOR = {
  draft: 'bg-gray-200', scheduled: 'bg-blue-200', running: 'bg-amber-200',
  paused: 'bg-yellow-200', completed: 'bg-green-200', failed: 'bg-red-200',
}

export default function Campaigns() {
  const { data, isLoading } = useQuery({ queryKey: ['camps'], queryFn: () => api.get('/api/v1/campaigns/') })
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <Link to="/campaigns/new" className="bg-indigo-600 text-white rounded px-3 py-1 text-sm">+ New campaign</Link>
      </div>
      {isLoading ? <div>Loading…</div> : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="text-left px-3 py-2">Name</th>
                <th className="text-left px-3 py-2">Status</th>
                <th className="text-left px-3 py-2">Segment</th>
                <th className="text-left px-3 py-2">Channel</th>
                <th className="text-right px-3 py-2">Sent</th>
                <th className="text-right px-3 py-2">Delivered</th>
                <th className="text-right px-3 py-2">Clicked</th>
              </tr>
            </thead>
            <tbody>
              {(data?.results || []).map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="px-3 py-2"><Link to={`/campaigns/${c.id}`} className="text-indigo-600">{c.name}</Link></td>
                  <td className="px-3 py-2"><span className={`px-2 py-0.5 rounded text-xs ${STATUS_COLOR[c.status]}`}>{c.status}</span></td>
                  <td className="px-3 py-2">{c.segment_name}</td>
                  <td className="px-3 py-2">{c.channel}</td>
                  <td className="px-3 py-2 text-right">{c.stat_sent}</td>
                  <td className="px-3 py-2 text-right">{c.stat_delivered}</td>
                  <td className="px-3 py-2 text-right">{c.stat_clicked}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

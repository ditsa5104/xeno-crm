import React from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Megaphone } from 'lucide-react'
import { api } from '../api/client.js'
import PageHeader from '../components/PageHeader.jsx'
import { SkeletonRow } from '../components/Skeleton.jsx'
import EmptyState from '../components/EmptyState.jsx'

const STATUS_STYLE = {
  draft: 'bg-slate-100 text-slate-700 ring-slate-200',
  scheduled: 'bg-blue-50 text-blue-700 ring-blue-200',
  running: 'bg-amber-50 text-amber-700 ring-amber-200',
  paused: 'bg-yellow-50 text-yellow-700 ring-yellow-200',
  completed: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  failed: 'bg-red-50 text-red-700 ring-red-200',
}

export default function Campaigns() {
  const { data, isLoading } = useQuery({ queryKey: ['camps'], queryFn: () => api.get('/api/v1/campaigns/') })
  const rows = data?.results || []

  return (
    <div>
      <PageHeader
        title="Campaigns"
        subtitle={data ? `${data.count} total` : undefined}
        actions={
          <Link to="/campaigns/new" className="btn-gradient">
            <Plus className="w-4 h-4" /> New campaign
          </Link>
        }
      />

      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 tracking-wide">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Status</th>
              <th className="text-left px-4 py-3 font-medium">Segment</th>
              <th className="text-left px-4 py-3 font-medium">Channel</th>
              <th className="text-right px-4 py-3 font-medium">Sent</th>
              <th className="text-right px-4 py-3 font-medium">Delivered</th>
              <th className="text-right px-4 py-3 font-medium">Clicked</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} cols={7} />)
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={7}>
                  <EmptyState
                    icon={Megaphone}
                    title="No campaigns yet"
                    description="Create your first campaign to start engaging customers."
                    action={<Link to="/campaigns/new" className="btn-gradient"><Plus className="w-4 h-4" /> New campaign</Link>}
                  />
                </td>
              </tr>
            ) : (
              rows.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition">
                  <td className="px-4 py-3">
                    <Link to={`/campaigns/${c.id}`} className="font-medium text-slate-900 hover:text-indigo-600">{c.name}</Link>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`chip ring-1 ${STATUS_STYLE[c.status] || STATUS_STYLE.draft}`}>{c.status}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{c.segment_name}</td>
                  <td className="px-4 py-3 capitalize text-slate-600">{c.channel}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{c.stat_sent}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{c.stat_delivered}</td>
                  <td className="px-4 py-3 text-right tabular-nums font-medium">{c.stat_clicked}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

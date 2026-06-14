import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Search, Users, Phone } from 'lucide-react'
import { api } from '../api/client.js'
import RFMBadge from '../components/RFMBadge.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { SkeletonRow } from '../components/Skeleton.jsx'
import EmptyState from '../components/EmptyState.jsx'
import InsightPanel from '../components/InsightPanel.jsx'

export default function Customers() {
  const [q, setQ] = useState('')
  const [insight, setInsight] = useState(false)
  const { data, isLoading } = useQuery({
    queryKey: ['customers', q],
    queryFn: () => api.get(`/api/v1/customers/?search=${encodeURIComponent(q)}`),
  })

  const rows = data?.results || []

  return (
    <div>
      <PageHeader
        title="Customers"
        subtitle={data ? `${data.count} total` : undefined}
        actions={
          <div className="flex items-center gap-2">
            <button onClick={() => setInsight(true)} className="btn-gradient whitespace-nowrap">
              <Phone className="w-4 h-4" /> Who do I talk to today?
            </button>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                className="input pl-9 w-64"
                placeholder="Search by name, email, city…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
              />
            </div>
          </div>
        }
      />

      {insight && (
        <InsightPanel
          insightKey="who_to_contact_today"
          title="Who do I talk to today?"
          onClose={() => setInsight(false)}
        />
      )}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wide">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Email</th>
              <th className="text-left px-4 py-3 font-medium">City</th>
              <th className="text-left px-4 py-3 font-medium">Tier</th>
              <th className="text-right px-4 py-3 font-medium">Spend</th>
              <th className="text-right px-4 py-3 font-medium">Orders</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              Array.from({ length: 8 }).map((_, i) => <SkeletonRow key={i} cols={6} />)
            ) : rows.length === 0 ? (
              <tr><td colSpan={6}><EmptyState icon={Users} title="No customers found" description="Try a different search, or import a CSV." /></td></tr>
            ) : (
              rows.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition">
                  <td className="px-4 py-3">
                    <Link to={`/customers/${c.id}`} className="font-medium text-slate-900 hover:text-emerald-600">{c.name}</Link>
                  </td>
                  <td className="px-4 py-3 text-slate-500">{c.email || '—'}</td>
                  <td className="px-4 py-3 text-slate-700">{c.city || '—'}</td>
                  <td className="px-4 py-3"><RFMBadge tier={c.rfm_tier} /></td>
                  <td className="px-4 py-3 text-right tabular-nums font-medium">₹{Number(c.total_spend).toLocaleString('en-IN')}</td>
                  <td className="px-4 py-3 text-right tabular-nums text-slate-600">{c.total_orders}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

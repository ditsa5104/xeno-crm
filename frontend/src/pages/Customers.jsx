import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'
import RFMBadge from '../components/RFMBadge.jsx'

export default function Customers() {
  const [q, setQ] = useState('')
  const { data, isLoading } = useQuery({
    queryKey: ['customers', q],
    queryFn: () => api.get(`/api/v1/customers/?search=${encodeURIComponent(q)}`),
  })
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Customers</h1>
        <input
          className="border rounded px-2 py-1 text-sm"
          placeholder="Search…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </div>
      {isLoading ? <div>Loading…</div> : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th className="text-left px-3 py-2">Name</th>
                <th className="text-left px-3 py-2">Email</th>
                <th className="text-left px-3 py-2">City</th>
                <th className="text-left px-3 py-2">Tier</th>
                <th className="text-right px-3 py-2">Spend</th>
                <th className="text-right px-3 py-2">Orders</th>
              </tr>
            </thead>
            <tbody>
              {(data?.results || []).map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="px-3 py-2"><Link to={`/customers/${c.id}`} className="text-indigo-600">{c.name}</Link></td>
                  <td className="px-3 py-2 text-gray-500">{c.email}</td>
                  <td className="px-3 py-2">{c.city}</td>
                  <td className="px-3 py-2"><RFMBadge tier={c.rfm_tier} /></td>
                  <td className="px-3 py-2 text-right">₹{c.total_spend}</td>
                  <td className="px-3 py-2 text-right">{c.total_orders}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

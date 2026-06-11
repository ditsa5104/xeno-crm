import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client.js'
import FilterBuilder from '../components/FilterBuilder.jsx'

export default function Segments() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['segs'], queryFn: () => api.get('/api/v1/segments/') })
  const [name, setName] = useState('')
  const [tree, setTree] = useState({ operator: 'AND', conditions: [] })
  const [nlInput, setNlInput] = useState('')

  const createSeg = useMutation({
    mutationFn: () => api.post('/api/v1/segments/', { name, segment_type: 'dynamic', filter_tree: tree }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['segs'] }); setName('') },
  })
  const aiBuild = useMutation({
    mutationFn: () => api.post('/api/v1/segments/ai-build/', { name: name || 'AI segment', nl_filter: nlInput }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['segs'] }); setNlInput('') },
  })

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Segments</h1>

      <div className="bg-white rounded-lg border p-4 space-y-3">
        <h2 className="font-semibold">Build with AI</h2>
        <div className="flex gap-2">
          <input
            className="border rounded px-2 py-1 flex-1 text-sm"
            placeholder="e.g. high-value customers from Mumbai who haven't bought in 3 months"
            value={nlInput}
            onChange={(e) => setNlInput(e.target.value)}
          />
          <input className="border rounded px-2 py-1 text-sm w-40" placeholder="Segment name" value={name} onChange={(e) => setName(e.target.value)} />
          <button
            onClick={() => aiBuild.mutate()}
            disabled={!nlInput}
            className="bg-indigo-600 text-white px-3 rounded text-sm disabled:opacity-50"
          >✨ Build</button>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-4 space-y-3">
        <h2 className="font-semibold">Build manually</h2>
        <FilterBuilder value={tree} onChange={setTree} />
        <button onClick={() => createSeg.mutate()} disabled={!name} className="bg-indigo-600 text-white rounded px-3 py-1 text-sm disabled:opacity-50">Create segment</button>
      </div>

      <div className="bg-white rounded-lg border overflow-hidden">
        {isLoading ? <div className="p-4">Loading…</div> : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr><th className="text-left px-3 py-2">Name</th><th className="text-left px-3 py-2">Type</th><th className="text-right px-3 py-2">Count</th><th className="text-left px-3 py-2">AI?</th></tr>
            </thead>
            <tbody>
              {(data?.results || []).map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="px-3 py-2">{s.name}</td>
                  <td className="px-3 py-2">{s.segment_type}</td>
                  <td className="px-3 py-2 text-right">{s.customer_count}</td>
                  <td className="px-3 py-2">{s.ai_generated ? '✨' : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

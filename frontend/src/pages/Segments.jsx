import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Sparkles, Loader2, Wand2, Layers } from 'lucide-react'
import { api } from '../api/client.js'
import FilterBuilder from '../components/FilterBuilder.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { SkeletonRow } from '../components/Skeleton.jsx'
import EmptyState from '../components/EmptyState.jsx'

export default function Segments() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['segs'], queryFn: () => api.get('/api/v1/segments/') })
  const [name, setName] = useState('')
  const [tree, setTree] = useState({ operator: 'AND', conditions: [] })
  const [nlInput, setNlInput] = useState('')

  const createSeg = useMutation({
    mutationFn: () => api.post('/api/v1/segments/', { name, segment_type: 'dynamic', filter_tree: tree }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['segs'] }); setName(''); setTree({ operator: 'AND', conditions: [] }) },
  })
  const aiBuild = useMutation({
    mutationFn: () => api.post('/api/v1/segments/ai-build/', { name: name || 'AI segment', nl_filter: nlInput }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['segs'] }); setNlInput(''); setName('') },
  })

  const rows = data?.results || []

  return (
    <div className="space-y-6">
      <PageHeader title="Segments" subtitle="Group customers using filters or natural language." />

      <div className="card p-5 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-emerald-500/5 to-teal-500/5 pointer-events-none" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-600 to-teal-500 grid place-items-center text-white">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="font-semibold">Build with AI</div>
              <div className="text-xs text-slate-500">Describe your audience in plain English.</div>
            </div>
          </div>
          <div className="flex flex-col md:flex-row gap-2">
            <input
              className="input flex-1"
              placeholder="High-value customers from Mumbai who haven't bought in 3 months"
              value={nlInput}
              onChange={(e) => setNlInput(e.target.value)}
            />
            <input className="input md:w-48" placeholder="Segment name" value={name} onChange={(e) => setName(e.target.value)} />
            <button
              onClick={() => aiBuild.mutate()}
              disabled={!nlInput || aiBuild.isPending}
              className="btn-gradient whitespace-nowrap"
            >
              {aiBuild.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Build with AI
            </button>
          </div>
        </div>
      </div>

      <div className="card p-5">
        <div className="flex items-center gap-2 mb-3">
          <Wand2 className="w-4 h-4 text-slate-500" />
          <div className="font-semibold">Or build manually</div>
        </div>
        <FilterBuilder value={tree} onChange={setTree} />
        <div className="mt-4 flex gap-2">
          <input className="input md:w-64" placeholder="Segment name" value={name} onChange={(e) => setName(e.target.value)} />
          <button onClick={() => createSeg.mutate()} disabled={!name || createSeg.isPending} className="btn-primary">
            {createSeg.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Create segment
          </button>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-100 font-semibold text-sm">Existing segments</div>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500 tracking-wide">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Type</th>
              <th className="text-right px-4 py-3 font-medium">Customers</th>
              <th className="text-left px-4 py-3 font-medium">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} cols={4} />)
            ) : rows.length === 0 ? (
              <tr><td colSpan={4}><EmptyState icon={Layers} title="No segments yet" description="Build your first segment above." /></td></tr>
            ) : (
              rows.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50 transition">
                  <td className="px-4 py-3 font-medium text-slate-900">{s.name}</td>
                  <td className="px-4 py-3"><span className="chip bg-slate-100 text-slate-700">{s.segment_type}</span></td>
                  <td className="px-4 py-3 text-right tabular-nums font-medium">{s.customer_count}</td>
                  <td className="px-4 py-3">
                    {s.ai_generated
                      ? <span className="chip bg-gradient-to-r from-emerald-50 to-teal-50 text-emerald-700 ring-1 ring-emerald-200"><Sparkles className="w-3 h-3" />AI</span>
                      : <span className="text-xs text-slate-400">Manual</span>}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

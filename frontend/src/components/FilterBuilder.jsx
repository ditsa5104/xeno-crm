import React from 'react'
import { Plus, X, FolderPlus } from 'lucide-react'

const FIELDS = [
  'total_spend', 'total_orders', 'last_order_at', 'rfm_recency_score',
  'rfm_frequency_score', 'rfm_monetary_score', 'rfm_composite', 'rfm_tier',
  'churn_risk_score', 'city', 'gender', 'channel_preference', 'tags',
]
const OPS = ['gte', 'lte', 'gt', 'lt', 'eq', 'in', 'days_ago_lte', 'days_ago_gte', 'contains', 'contains_any']

export default function FilterBuilder({ value, onChange, depth = 0 }) {
  const node = value || { operator: 'AND', conditions: [] }
  const isGroup = !!node.conditions

  if (!isGroup) {
    return (
      <div className="flex gap-2 items-center bg-white">
        <select
          className="rounded-md border border-slate-200 px-2 py-1 text-xs bg-white outline-none focus:border-indigo-500"
          value={node.field || ''}
          onChange={(e) => onChange({ ...node, field: e.target.value })}
        >
          <option value="">— field —</option>
          {FIELDS.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
        <select
          className="rounded-md border border-slate-200 px-2 py-1 text-xs bg-white outline-none focus:border-indigo-500"
          value={node.op || ''}
          onChange={(e) => onChange({ ...node, op: e.target.value })}
        >
          <option value="">op</option>
          {OPS.map((o) => <option key={o} value={o}>{o}</option>)}
        </select>
        <input
          className="rounded-md border border-slate-200 px-2 py-1 text-xs flex-1 outline-none focus:border-indigo-500"
          placeholder="value"
          value={node.value ?? ''}
          onChange={(e) => onChange({ ...node, value: e.target.value })}
        />
      </div>
    )
  }

  const update = (i, child) => {
    const cs = [...node.conditions]
    cs[i] = child
    onChange({ ...node, conditions: cs })
  }
  const remove = (i) => {
    const cs = [...node.conditions]
    cs.splice(i, 1)
    onChange({ ...node, conditions: cs })
  }

  const borderColor = depth % 2 ? 'border-purple-200 bg-purple-50/30' : 'border-indigo-200 bg-indigo-50/30'

  return (
    <div className={`rounded-lg border-l-4 ${borderColor} pl-4 pr-3 py-3`}>
      <div className="flex gap-2 items-center mb-3 flex-wrap">
        <div className="inline-flex rounded-md border border-slate-200 bg-white text-xs overflow-hidden">
          {['AND', 'OR'].map((op) => (
            <button
              key={op}
              onClick={() => onChange({ ...node, operator: op })}
              className={`px-2.5 py-1 font-medium transition ${
                node.operator === op ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'
              }`}
            >{op}</button>
          ))}
        </div>
        <button
          onClick={() => onChange({ ...node, conditions: [...node.conditions, { field: '', op: 'eq', value: '' }] })}
          className="btn-secondary text-xs py-1"
        >
          <Plus className="w-3 h-3" /> Condition
        </button>
        <button
          onClick={() => onChange({ ...node, conditions: [...node.conditions, { operator: 'AND', conditions: [] }] })}
          className="btn-secondary text-xs py-1"
        >
          <FolderPlus className="w-3 h-3" /> Group
        </button>
      </div>
      <div className="space-y-2">
        {node.conditions.map((c, i) => (
          <div key={i} className="flex gap-2 items-start">
            <div className="flex-1">
              <FilterBuilder value={c} onChange={(nc) => update(i, nc)} depth={depth + 1} />
            </div>
            <button onClick={() => remove(i)} className="text-slate-400 hover:text-red-500 p-1 rounded hover:bg-red-50 transition">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
        {node.conditions.length === 0 && (
          <div className="text-xs text-slate-400 italic py-1">Empty group — add a condition above.</div>
        )}
      </div>
    </div>
  )
}

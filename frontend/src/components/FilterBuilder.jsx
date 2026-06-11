import React from 'react'

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
      <div className="flex gap-2 items-center">
        <select
          className="border rounded px-1 py-0.5 text-xs"
          value={node.field || ''}
          onChange={(e) => onChange({ ...node, field: e.target.value })}
        >
          <option value="">field</option>
          {FIELDS.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
        <select
          className="border rounded px-1 py-0.5 text-xs"
          value={node.op || ''}
          onChange={(e) => onChange({ ...node, op: e.target.value })}
        >
          <option value="">op</option>
          {OPS.map((o) => <option key={o} value={o}>{o}</option>)}
        </select>
        <input
          className="border rounded px-1 py-0.5 text-xs flex-1"
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

  return (
    <div className={`border-l-4 pl-3 py-2 ${depth % 2 ? 'border-purple-300' : 'border-indigo-300'}`}>
      <div className="flex gap-2 items-center mb-2">
        <select
          className="border rounded px-1 py-0.5 text-xs"
          value={node.operator}
          onChange={(e) => onChange({ ...node, operator: e.target.value })}
        >
          <option value="AND">AND</option>
          <option value="OR">OR</option>
        </select>
        <button
          onClick={() => onChange({ ...node, conditions: [...node.conditions, { field: '', op: 'eq', value: '' }] })}
          className="text-xs bg-gray-100 rounded px-2 py-0.5"
        >+ condition</button>
        <button
          onClick={() => onChange({ ...node, conditions: [...node.conditions, { operator: 'AND', conditions: [] }] })}
          className="text-xs bg-gray-100 rounded px-2 py-0.5"
        >+ group</button>
      </div>
      <div className="space-y-2">
        {node.conditions.map((c, i) => (
          <div key={i} className="flex gap-1 items-start">
            <div className="flex-1">
              <FilterBuilder value={c} onChange={(nc) => update(i, nc)} depth={depth + 1} />
            </div>
            <button onClick={() => remove(i)} className="text-xs text-red-500">×</button>
          </div>
        ))}
      </div>
    </div>
  )
}

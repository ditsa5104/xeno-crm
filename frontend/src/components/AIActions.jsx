import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Phone, Undo2, Crown, TrendingUp, Sparkles, Clock } from 'lucide-react'
import { api } from '../api/client.js'
import InsightPanel from './InsightPanel.jsx'

const ICONS = {
  phone: Phone,
  undo: Undo2,
  crown: Crown,
  'trending-up': TrendingUp,
}

const fmtHour = (h) => {
  const am = h < 12
  const hr = h % 12 === 0 ? 12 : h % 12
  return `${hr} ${am ? 'AM' : 'PM'}`
}

/**
 * A row of one-tap AI action buttons ("Who do I talk to today?", etc). Each opens
 * an InsightPanel with data-grounded recommendations and an AI playbook — so the
 * marketer gets AI-driven next steps without typing into the assistant.
 */
export default function AIActions() {
  const { data } = useQuery({ queryKey: ['insight-catalogue'], queryFn: () => api.get('/api/v1/analytics/insights/') })
  const [active, setActive] = React.useState(null)

  const insights = data?.insights || []
  const window = data?.best_send_window

  return (
    <div className="card p-5 relative overflow-hidden">
      <div className="absolute -right-8 -top-8 w-32 h-32 rounded-full bg-gradient-to-br from-brand-500/10 to-transparent blur-2xl pointer-events-none" />
      <div className="relative">
        <div className="flex items-center justify-between mb-3.5">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-600 to-teal-500 grid place-items-center text-white">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <h2 className="font-semibold text-slate-800">AI actions</h2>
          </div>
          {window && (
            <span className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 bg-slate-50 px-2.5 py-1 rounded-full ring-1 ring-slate-200/70">
              <Clock className="w-3.5 h-3.5 text-brand-500" />
              Best send time ≈ <span className="font-semibold text-slate-700">{fmtHour(window.recommended_hour)}</span>
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {insights.map((ins) => {
            const Icon = ICONS[ins.icon] || Sparkles
            return (
              <button
                key={ins.key}
                onClick={() => setActive(ins)}
                className="group text-left rounded-xl border border-slate-200 p-3.5 hover:border-brand-300 hover:bg-brand-50/40 hover:shadow-soft transition-all"
              >
                <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500/10 to-teal-500/10 text-brand-600 grid place-items-center mb-2.5 group-hover:scale-110 transition-transform">
                  <Icon className="w-[18px] h-[18px]" />
                </div>
                <div className="text-sm font-semibold text-slate-800 leading-snug">{ins.label}</div>
                <div className="text-xs text-brand-600 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">Run insight →</div>
              </button>
            )
          })}
        </div>
      </div>

      {active && (
        <InsightPanel
          insightKey={active.key}
          title={active.label}
          onClose={() => setActive(null)}
        />
      )}
    </div>
  )
}

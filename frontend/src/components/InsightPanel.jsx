import React from 'react'
import { useNavigate } from 'react-router-dom'
import { X, Sparkles, Loader2, ArrowRight, Phone, Mail } from 'lucide-react'
import { api } from '../api/client.js'
import Markdown from './Markdown.jsx'
import RFMBadge from './RFMBadge.jsx'

const inr = (v) => '₹' + Number(v || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })

/**
 * Slide-over panel that runs an AI action insight (e.g. "who to contact today"),
 * shows the data-grounded recommended customers + an AI playbook, and lets the
 * marketer act on the group without leaving the page.
 */
export default function InsightPanel({ insightKey, title, onClose }) {
  const [data, setData] = React.useState(null)
  const [error, setError] = React.useState('')
  const nav = useNavigate()

  React.useEffect(() => {
    let cancelled = false
    setData(null); setError('')
    api.get(`/api/v1/analytics/insights/${insightKey}/`)
      .then((d) => { if (!cancelled) setData(d) })
      .catch((e) => { if (!cancelled) setError(e.message || 'Failed to load insight') })
    return () => { cancelled = true }
  }, [insightKey])

  const customers = data?.customers || []

  return (
    <>
      <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 animate-fade-in" onClick={onClose} />
      <div className="fixed top-0 right-0 h-full w-[460px] max-w-full bg-white shadow-lift flex flex-col z-50 animate-scale-in origin-right">
        <div className="px-5 py-4 border-b border-slate-100 flex items-start justify-between bg-gradient-to-b from-brand-50/60 to-transparent">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 grid place-items-center text-white shadow-glow">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="font-bold leading-none">{data?.title || title}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">AI recommendation</div>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-700 p-1.5 rounded-lg hover:bg-slate-100 transition">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {error && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">{error}</div>}

          {!data && !error && (
            <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-3">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="text-sm">Analysing your customers…</span>
            </div>
          )}

          {data && (
            <>
              {data.subtitle && <p className="text-sm text-slate-500">{data.subtitle}</p>}

              {/* AI playbook */}
              {data.playbook && (
                <div className="rounded-xl border border-brand-200/70 bg-brand-50/40 p-3.5">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-brand-700 mb-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> AI playbook
                  </div>
                  <div className="text-slate-700"><Markdown content={data.playbook} /></div>
                </div>
              )}

              {/* Recommended customers */}
              <div>
                <div className="eyebrow mb-2">{customers.length} recommended</div>
                <ul className="space-y-2">
                  {customers.map((c) => (
                    <li key={c.id} className="rounded-xl border border-slate-200 p-3 hover:border-brand-300 hover:shadow-soft transition-all">
                      <div className="flex items-center justify-between gap-2">
                        <button
                          onClick={() => { onClose(); nav(`/customers/${c.id}`) }}
                          className="font-semibold text-slate-900 hover:text-brand-600 text-sm truncate"
                        >
                          {c.name}
                        </button>
                        <RFMBadge tier={c.rfm_tier} />
                      </div>
                      <div className="text-xs text-slate-500 mt-1">{c.reason}</div>
                      <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                        <span>{inr(c.total_spend)} lifetime</span>
                        <span>·</span>
                        <span>{c.total_orders} orders</span>
                        {c.phone && <span className="ml-auto flex items-center gap-1 text-slate-500"><Phone className="w-3 h-3" /> {c.channel_preference}</span>}
                        {!c.phone && c.email && <span className="ml-auto flex items-center gap-1 text-slate-500"><Mail className="w-3 h-3" /> email</span>}
                      </div>
                    </li>
                  ))}
                </ul>
                {customers.length === 0 && (
                  <div className="text-sm text-slate-400 text-center py-8">No customers match this right now — that's good news.</div>
                )}
              </div>
            </>
          )}
        </div>

        {data && customers.length > 0 && (
          <div className="border-t border-slate-100 p-4">
            <button
              onClick={() => { onClose(); nav('/campaigns/new') }}
              className="btn-gradient w-full justify-center"
            >
              Create a campaign for this group <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </>
  )
}

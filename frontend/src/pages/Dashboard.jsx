import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { api } from '../api/client.js'
import { Users, Send, CheckCircle2, MailOpen, IndianRupee } from 'lucide-react'
import LiveEventFeed from '../components/LiveEventFeed.jsx'
import PageHeader from '../components/PageHeader.jsx'
import { CardSkeleton } from '../components/Skeleton.jsx'
import AIActions from '../components/AIActions.jsx'
import { useAuth } from '../contexts/AuthContext.jsx'

const CHANNEL_COLOR = {
  whatsapp: '#10B981',
  email: '#3B82F6',
  sms: '#6B7280',
  rcs: '#0d9488',
  auto: '#059669',
}

const STATUS_BADGE = {
  draft: 'bg-slate-100 text-slate-600',
  scheduled: 'bg-amber-100 text-amber-700',
  running: 'bg-emerald-100 text-emerald-700',
  paused: 'bg-amber-100 text-amber-700',
  completed: 'bg-emerald-100 text-emerald-700',
  failed: 'bg-red-100 text-red-700',
}

const pct = (v) => `${((v || 0) * 100).toFixed(1)}%`
const inr = (v) =>
  '₹' + Number(v || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })

const METRIC_STYLES = {
  customers: { bg: 'from-blue-50 to-white', ring: 'bg-blue-100/70 text-blue-600' },
  campaigns: { bg: 'from-teal-50 to-white', ring: 'bg-teal-100/70 text-teal-600' },
  delivered: { bg: 'from-emerald-50 to-white', ring: 'bg-emerald-100/70 text-emerald-600' },
  open: { bg: 'from-amber-50 to-white', ring: 'bg-amber-100/70 text-amber-600' },
  revenue: { bg: 'from-rose-50 to-white', ring: 'bg-rose-100/70 text-rose-600' },
}

function MetricCard({ label, value, tone = 'customers', icon: Icon }) {
  const s = METRIC_STYLES[tone] || METRIC_STYLES.customers
  return (
    <div className={`rounded-2xl border border-slate-200/60 p-5 bg-gradient-to-br ${s.bg} shadow-card card-hover group`}>
      <div className="flex items-center justify-between">
        <div className="eyebrow">{label}</div>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg ${s.ring} grid place-items-center group-hover:scale-110 transition-transform`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="text-[28px] font-extrabold mt-2.5 text-slate-900 tabular-nums">{value}</div>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => api.get('/api/v1/analytics/overview/'),
  })

  const firstName = user?.name?.split(' ')[0] || user?.username
  const s = data?.summary

  return (
    <div>
      <PageHeader
        title={firstName ? `Welcome back, ${firstName} 👋` : 'Dashboard'}
        subtitle="Here's a snapshot of your CRM today."
      />

      {error && (
        <div className="card p-4 mb-6 border-red-200 bg-red-50 text-red-700 text-sm">{error.message}</div>
      )}

      {/* Top metrics strip */}
      <div data-tour="metrics" className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {isLoading || !s ? (
          Array.from({ length: 5 }).map((_, i) => <CardSkeleton key={i} height="h-28" />)
        ) : (
          <>
            <MetricCard label="Total Customers" value={s.total_customers} tone="customers" icon={Users} />
            <MetricCard label="Campaigns Sent" value={s.campaigns_total} tone="campaigns" icon={Send} />
            <MetricCard label="Messages Delivered" value={s.messages_delivered} tone="delivered" icon={CheckCircle2} />
            <MetricCard label="Avg Open Rate" value={pct(s.overall_open_rate)} tone="open" icon={MailOpen} />
            <MetricCard label="Revenue Attributed" value={inr(s.total_revenue_attributed)} tone="revenue" icon={IndianRupee} />
          </>
        )}
      </div>

      {/* AI actions — one-tap, data-grounded next steps */}
      <div className="mt-6">
        <AIActions />
      </div>

      {/* Main grid: recent campaigns + top segments */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mt-6">
        <div className="lg:col-span-3 card p-5">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Recent Campaigns</h2>
          {isLoading ? (
            <CardSkeleton height="h-48" />
          ) : data?.recent_campaigns?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100">
                    <th className="py-2 pr-3 font-medium">Campaign</th>
                    <th className="py-2 px-3 font-medium">Channel</th>
                    <th className="py-2 px-3 font-medium">Sent</th>
                    <th className="py-2 px-3 font-medium">Open Rate</th>
                    <th className="py-2 pl-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_campaigns.map((c) => (
                    <tr key={c.id} className="border-b border-slate-50 hover:bg-slate-50/60">
                      <td className="py-2.5 pr-3">
                        <Link to={`/campaigns/${c.id}`} className="font-medium text-slate-800 hover:text-emerald-600">
                          {c.name}
                        </Link>
                        <div className="text-xs text-slate-400">{c.segment_name}</div>
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="inline-flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full" style={{ background: CHANNEL_COLOR[c.channel] || '#6B7280' }} />
                          <span className="capitalize text-slate-600">{c.channel}</span>
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-600">{c.sent}</td>
                      <td className="py-2.5 px-3 text-slate-600">{pct(c.open_rate)}</td>
                      <td className="py-2.5 pl-3">
                        <span className={`chip ${STATUS_BADGE[c.status] || 'bg-slate-100 text-slate-600'} capitalize`}>
                          {c.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-slate-400 py-8 text-center">No campaigns yet.</p>
          )}
        </div>

        <div className="lg:col-span-2 card p-5">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Top Performing Segments</h2>
          {isLoading ? (
            <CardSkeleton height="h-48" />
          ) : data?.top_segments?.length ? (
            <ul className="space-y-3">
              {data.top_segments.map((seg) => (
                <li key={seg.id}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700 truncate">{seg.name}</span>
                    <span className="text-slate-500">{pct(seg.engagement_rate)}</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-500"
                      style={{ width: `${Math.min(100, (seg.engagement_rate || 0) * 100)}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-400 py-8 text-center">No engagement data yet.</p>
          )}
        </div>
      </div>

      {/* Performance chart */}
      <div className="card p-5 mt-6">
        <h2 className="text-base font-semibold text-slate-800 mb-4">Campaign Performance — Last 30 Days</h2>
        {isLoading ? (
          <CardSkeleton height="h-72" />
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={data?.performance || []} margin={{ left: 0, right: 12, top: 8, bottom: 4 }}>
              <defs>
                <linearGradient id="gSent" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gOpened" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gClicked" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0d9488" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0d9488" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis
                dataKey="date" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false}
                tickFormatter={(d) => d?.slice(5)}
                minTickGap={24}
              />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Area type="monotone" dataKey="sent" stroke="#059669" fill="url(#gSent)" strokeWidth={2} name="Sent" />
              <Area type="monotone" dataKey="opened" stroke="#10B981" fill="url(#gOpened)" strokeWidth={2} name="Opened" />
              <Area type="monotone" dataKey="clicked" stroke="#0d9488" fill="url(#gClicked)" strokeWidth={2} name="Clicked" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="mt-6">
        <LiveEventFeed />
      </div>
    </div>
  )
}

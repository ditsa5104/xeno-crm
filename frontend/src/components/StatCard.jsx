import React from 'react'

export default function StatCard({ label, value, icon: Icon, accent = 'indigo', delta }) {
  const accents = {
    indigo: 'from-indigo-500/10 to-indigo-500/0 text-indigo-600',
    purple: 'from-purple-500/10 to-purple-500/0 text-purple-600',
    pink: 'from-pink-500/10 to-pink-500/0 text-pink-600',
    emerald: 'from-emerald-500/10 to-emerald-500/0 text-emerald-600',
    amber: 'from-amber-500/10 to-amber-500/0 text-amber-600',
  }
  return (
    <div className="card p-5 relative overflow-hidden card-hover">
      <div className={`absolute inset-0 bg-gradient-to-br ${accents[accent]} opacity-50 pointer-events-none`} />
      <div className="relative">
        <div className="flex items-center justify-between">
          <div className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</div>
          {Icon && <Icon className={`w-4 h-4 ${accents[accent].split(' ').pop()}`} />}
        </div>
        <div className="text-3xl font-bold mt-2 text-slate-900">{value}</div>
        {delta !== undefined && (
          <div className={`text-xs mt-1 ${delta >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
            {delta >= 0 ? '↑' : '↓'} {Math.abs(delta)}%
          </div>
        )}
      </div>
    </div>
  )
}

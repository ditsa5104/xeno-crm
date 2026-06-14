import React from 'react'

export default function StatCard({ label, value, icon: Icon, accent = 'indigo', delta }) {
  const accents = {
    indigo: { grad: 'from-emerald-500/10 to-transparent', icon: 'text-emerald-600', ring: 'bg-emerald-50' },
    purple: { grad: 'from-teal-500/10 to-transparent', icon: 'text-teal-600', ring: 'bg-teal-50' },
    pink: { grad: 'from-green-500/10 to-transparent', icon: 'text-green-600', ring: 'bg-green-50' },
    emerald: { grad: 'from-emerald-500/10 to-transparent', icon: 'text-emerald-600', ring: 'bg-emerald-50' },
    amber: { grad: 'from-amber-500/10 to-transparent', icon: 'text-amber-600', ring: 'bg-amber-50' },
  }
  const a = accents[accent] || accents.indigo
  return (
    <div className="card p-5 relative overflow-hidden card-hover group">
      <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full bg-gradient-to-br ${a.grad} blur-2xl pointer-events-none`} />
      <div className="relative">
        <div className="flex items-center justify-between">
          <div className="eyebrow">{label}</div>
          {Icon && (
            <div className={`w-8 h-8 rounded-lg ${a.ring} grid place-items-center ${a.icon} group-hover:scale-110 transition-transform`}>
              <Icon className="w-4 h-4" />
            </div>
          )}
        </div>
        <div className="text-[28px] font-extrabold mt-2.5 text-slate-900 tabular-nums">{value}</div>
        {delta !== undefined && (
          <div className={`text-xs mt-1 font-medium ${delta >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
            {delta >= 0 ? '↑' : '↓'} {Math.abs(delta)}%
          </div>
        )}
      </div>
    </div>
  )
}

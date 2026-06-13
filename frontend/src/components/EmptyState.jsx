import React from 'react'

export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="text-center py-14 px-4 animate-fade-up">
      {Icon && (
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-50 ring-1 ring-slate-200/60 grid place-items-center mx-auto mb-4 text-slate-400 shadow-soft">
          <Icon className="w-6 h-6" />
        </div>
      )}
      <div className="font-semibold text-slate-900">{title}</div>
      {description && <div className="text-sm text-slate-500 mt-1.5 max-w-sm mx-auto leading-relaxed">{description}</div>}
      {action && <div className="mt-5 flex justify-center">{action}</div>}
    </div>
  )
}

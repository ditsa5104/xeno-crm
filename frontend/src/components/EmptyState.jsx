import React from 'react'

export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="text-center py-12 px-4">
      {Icon && (
        <div className="w-12 h-12 rounded-full bg-slate-100 grid place-items-center mx-auto mb-3 text-slate-400">
          <Icon className="w-5 h-5" />
        </div>
      )}
      <div className="font-semibold text-slate-900">{title}</div>
      {description && <div className="text-sm text-slate-500 mt-1 max-w-sm mx-auto">{description}</div>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

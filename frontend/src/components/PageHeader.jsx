import React from 'react'

export default function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="flex items-start justify-between gap-4 mb-7">
      <div className="min-w-0">
        <h1 className="text-[26px] leading-tight font-extrabold tracking-tight text-white">{title}</h1>
        {subtitle && <p className="text-sm text-slate-400 mt-1.5">{subtitle}</p>}
      </div>
      {actions && <div className="flex gap-2 shrink-0">{actions}</div>}
    </div>
  )
}

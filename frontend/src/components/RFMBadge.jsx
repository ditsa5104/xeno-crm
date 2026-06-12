import React from 'react'

const TIER_STYLE = {
  Champions: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  Loyal: 'bg-green-50 text-green-700 ring-green-200',
  'Potential Loyalists': 'bg-lime-50 text-lime-700 ring-lime-200',
  'Recent Customers': 'bg-blue-50 text-blue-700 ring-blue-200',
  'At Risk': 'bg-amber-50 text-amber-700 ring-amber-200',
  'About to Lose': 'bg-orange-50 text-orange-700 ring-orange-200',
  Lost: 'bg-red-50 text-red-700 ring-red-200',
  Others: 'bg-slate-50 text-slate-600 ring-slate-200',
  Unscored: 'bg-slate-50 text-slate-400 ring-slate-200',
}

export default function RFMBadge({ tier }) {
  const cls = TIER_STYLE[tier] || TIER_STYLE.Unscored
  return (
    <span className={`chip ring-1 ${cls}`}>
      {tier || 'Unscored'}
    </span>
  )
}

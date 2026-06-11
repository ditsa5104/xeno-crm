import React from 'react'

const TIER_COLOR = {
  Champions: 'bg-emerald-500',
  Loyal: 'bg-green-500',
  'Potential Loyalists': 'bg-lime-500',
  'Recent Customers': 'bg-blue-500',
  'At Risk': 'bg-orange-500',
  'About to Lose': 'bg-red-400',
  Lost: 'bg-red-600',
  Others: 'bg-gray-400',
  Unscored: 'bg-gray-300',
}

export default function RFMBadge({ tier }) {
  return (
    <span className={`text-white text-xs px-2 py-0.5 rounded ${TIER_COLOR[tier] || 'bg-gray-400'}`}>
      {tier || 'Unscored'}
    </span>
  )
}

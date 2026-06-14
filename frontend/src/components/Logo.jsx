import React from 'react'

/**
 * Plume brand mark — a stylised feather/quill inside a rounded gradient tile.
 * The feather nods to both drafting a message (a quill) and sending it in flight
 * (a feather on the wind), which is exactly what the product does.
 */
export function LogoMark({ className = 'w-9 h-9', rounded = 'rounded-xl' }) {
  return (
    <span
      className={`${className} ${rounded} grid place-items-center text-white bg-[#11141a] ring-1 ring-white/10 shadow-soft`}
    >
      <svg viewBox="0 0 24 24" fill="none" className="w-[58%] h-[58%]" aria-hidden="true">
        {/* feather body */}
        <path
          d="M19 5c-6.5-1.2-11.5 2.4-13 9.5-.4 1.9-.5 3.4-.5 4.5"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="M19 5c1 5.5-1.3 10.2-6 12-2.2.85-4.4 1-6 .9C8.5 11.5 12.7 6.6 19 5Z"
          fill="white"
          fillOpacity="0.95"
        />
        {/* quill spine */}
        <path
          d="M16 8 8.5 16"
          stroke="#11141a"
          strokeWidth="1.3"
          strokeLinecap="round"
        />
      </svg>
    </span>
  )
}

/**
 * Full lockup: mark + wordmark. `tone` controls wordmark color for dark/light surfaces.
 */
export default function Logo({ size = 'md', tone = 'dark', showBadge = false }) {
  const markSize = size === 'lg' ? 'w-10 h-10' : 'w-9 h-9'
  const textSize = size === 'lg' ? 'text-2xl' : 'text-lg'
  const wordColor = tone === 'light' ? 'text-white' : 'text-slate-900'
  return (
    <span className="flex items-center gap-2.5">
      <LogoMark className={markSize} />
      <span className={`${textSize} font-extrabold tracking-tight ${wordColor}`}>Plume</span>
      {showBadge && (
        <span className="text-[10px] font-semibold uppercase tracking-wider text-brand-300 bg-brand-500/15 px-1.5 py-0.5 rounded-md">CRM</span>
      )}
    </span>
  )
}

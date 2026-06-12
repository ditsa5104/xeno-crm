import React from 'react'

export function SkeletonRow({ cols = 5 }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-4 py-3"><div className="skeleton h-4 w-3/4" /></td>
      ))}
    </tr>
  )
}

export function CardSkeleton({ height = 'h-24' }) {
  return <div className={`skeleton ${height} w-full`} />
}

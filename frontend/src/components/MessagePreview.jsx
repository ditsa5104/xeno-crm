import React from 'react'

export default function MessagePreview({ channel, body }) {
  return (
    <div className="bg-gray-50 rounded p-3 border text-sm">
      <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">{channel}</div>
      <div className="whitespace-pre-wrap">{body}</div>
    </div>
  )
}

import React, { useState } from 'react'
import { useCopilot } from '../contexts/CopilotContext.jsx'

export default function CopilotSidebar() {
  const { isOpen, setOpen, mode, setMode, messages, busy, send } = useCopilot()
  const [input, setInput] = useState('')

  if (!isOpen) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 bg-indigo-600 text-white rounded-full px-5 py-3 shadow-lg hover:bg-indigo-700"
      >
        ✨ Copilot
      </button>
    )
  }

  return (
    <div className="fixed top-0 right-0 h-full w-96 bg-white border-l border-gray-200 shadow-xl flex flex-col z-50">
      <div className="px-4 py-3 border-b flex items-center justify-between">
        <div>
          <div className="font-semibold">Xeno Copilot</div>
          <div className="flex gap-2 mt-1 text-xs">
            {['chat', 'agent'].map((m) => (
              <button
                key={m}
                className={`px-2 py-0.5 rounded ${mode === m ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}
                onClick={() => setMode(m)}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
        <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-700">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-sm text-gray-500">
            {mode === 'agent'
              ? 'Tell me a campaign goal and I\'ll prepare everything.'
              : 'Ask me about your customers, segments, or campaigns.'}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
            <div className={`inline-block max-w-[90%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
              m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-900'
            }`}>
              {m.content}
            </div>
            {m.meta?.tool_calls_made?.length > 0 && (
              <div className="text-[10px] text-gray-400 mt-1">tools: {m.meta.tool_calls_made.join(', ')}</div>
            )}
          </div>
        ))}
        {busy && <div className="text-sm text-gray-400">Thinking…</div>}
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); if (input.trim()) { send(input); setInput('') } }}
        className="p-3 border-t flex gap-2"
      >
        <input
          className="flex-1 border rounded px-2 py-1 text-sm"
          placeholder={mode === 'agent' ? 'Goal: re-engage Mumbai high-spenders…' : 'Ask anything…'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="bg-indigo-600 text-white rounded px-3 text-sm">Send</button>
      </form>
    </div>
  )
}

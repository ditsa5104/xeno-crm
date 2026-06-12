import React, { useEffect, useRef, useState } from 'react'
import { Sparkles, X, Send, MessageSquare, Wand2 } from 'lucide-react'
import { useCopilot } from '../contexts/CopilotContext.jsx'
import Markdown from './Markdown.jsx'

export default function CopilotSidebar() {
  const { isOpen, setOpen, mode, setMode, messages, busy, send } = useCopilot()
  const [input, setInput] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages, busy])

  if (!isOpen) return null

  const suggestions = mode === 'agent'
    ? ['Re-engage Mumbai high-spenders with a 15% off offer', 'Reactivate at-risk customers via WhatsApp', 'Upsell Champions on a new premium SKU']
    : ['How are my campaigns performing?', 'Which channel converts best?', 'Show me top customers by spend']

  return (
    <>
      <div className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40" onClick={() => setOpen(false)} />
      <div className="fixed top-0 right-0 h-full w-[420px] bg-white border-l border-slate-200 shadow-2xl flex flex-col z-50">
        <div className="px-5 py-4 border-b border-slate-200 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 grid place-items-center text-white">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="font-semibold">Xeno Copilot</div>
            </div>
            <div className="flex gap-1 mt-2.5 p-0.5 bg-slate-100 rounded-lg w-fit">
              {[
                { id: 'chat', label: 'Chat', icon: MessageSquare },
                { id: 'agent', label: 'Agent', icon: Wand2 },
              ].map((m) => {
                const Icon = m.icon
                return (
                  <button
                    key={m.id}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition ${
                      mode === m.id ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-700'
                    }`}
                    onClick={() => setMode(m.id)}
                  >
                    <Icon className="w-3.5 h-3.5" /> {m.label}
                  </button>
                )
              })}
            </div>
          </div>
          <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-700 p-1 rounded hover:bg-slate-100">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div className="space-y-3">
              <div className="text-sm text-slate-500">
                {mode === 'agent'
                  ? "Tell me a campaign goal and I'll plan everything end-to-end."
                  : 'Ask me about your customers, segments, or campaigns.'}
              </div>
              <div className="flex flex-col gap-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-left px-3 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-sm text-slate-700 transition"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}>
              <div className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm ${
                m.role === 'user'
                  ? 'bg-slate-900 text-white rounded-br-sm whitespace-pre-wrap'
                  : 'bg-slate-100 text-slate-900 rounded-bl-sm'
              }`}>
                {m.role === 'user' ? m.content : <Markdown content={m.content} />}
                {m.meta?.tool_calls_made?.length > 0 && (
                  <div className="text-[10px] text-slate-400 mt-1.5 pt-1.5 border-t border-slate-200/50">
                    🔧 {m.meta.tool_calls_made.join(' · ')}
                  </div>
                )}
              </div>
            </div>
          ))}
          {busy && (
            <div className="flex justify-start">
              <div className="bg-slate-100 rounded-2xl rounded-bl-sm px-3.5 py-2.5 text-sm flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); if (input.trim() && !busy) { send(input); setInput('') } }}
          className="p-4 border-t border-slate-200"
        >
          <div className="flex items-end gap-2 rounded-xl border border-slate-200 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100 bg-white p-2 transition">
            <textarea
              rows={1}
              className="flex-1 px-2 py-1 text-sm outline-none resize-none max-h-32"
              placeholder={mode === 'agent' ? 'Goal: re-engage Mumbai high-spenders…' : 'Ask anything…'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (input.trim() && !busy) { send(input); setInput('') } }
              }}
            />
            <button
              disabled={!input.trim() || busy}
              className="rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-2 hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:from-slate-300 disabled:to-slate-300"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="text-[10px] text-slate-400 mt-1.5 px-1">Enter to send · Shift+Enter for newline</div>
        </form>
      </div>
    </>
  )
}

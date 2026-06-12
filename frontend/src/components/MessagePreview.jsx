import React from 'react'
import { MessageSquare, Mail, Smartphone } from 'lucide-react'

const META = {
  whatsapp: { label: 'WhatsApp', icon: MessageSquare, accent: 'bg-emerald-500' },
  sms: { label: 'SMS', icon: Smartphone, accent: 'bg-blue-500' },
  email: { label: 'Email', icon: Mail, accent: 'bg-indigo-500' },
  rcs: { label: 'RCS', icon: MessageSquare, accent: 'bg-purple-500' },
  auto: { label: 'Auto', icon: MessageSquare, accent: 'bg-slate-500' },
}

export default function MessagePreview({ channel = 'whatsapp', body = '' }) {
  const meta = META[channel] || META.auto
  const Icon = meta.icon

  // Phone-style mock for whatsapp/sms/rcs; email envelope for email
  if (channel === 'email') {
    const lines = body.split('\n')
    const subjectLine = lines[0]?.startsWith('Subject:') ? lines[0].replace(/^Subject:\s*/, '') : '(No subject)'
    const bodyText = lines[0]?.startsWith('Subject:') ? lines.slice(1).join('\n') : body
    return (
      <div className="card overflow-hidden">
        <div className="px-4 py-2 border-b border-slate-200 bg-slate-50 flex items-center gap-2">
          <Icon className="w-4 h-4 text-indigo-500" />
          <span className="text-xs font-medium text-slate-600">{meta.label}</span>
        </div>
        <div className="p-5">
          <div className="text-xs text-slate-500 mb-1">From: Your Brand · &lt;hello@brand.com&gt;</div>
          <div className="text-base font-semibold text-slate-900 mb-3">{subjectLine}</div>
          <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{bodyText}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="card p-5 bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-6 h-6 rounded-md ${meta.accent} grid place-items-center text-white`}>
          <Icon className="w-3.5 h-3.5" />
        </div>
        <span className="text-xs font-medium text-slate-600">{meta.label}</span>
      </div>
      <div className="bg-white rounded-2xl rounded-tl-sm shadow-sm border border-slate-200 p-3 max-w-sm">
        <div className="text-sm whitespace-pre-wrap text-slate-800 leading-relaxed">{body || <span className="text-slate-400 italic">Your message will appear here…</span>}</div>
        <div className="text-[10px] text-slate-400 mt-2 text-right">delivered · just now</div>
      </div>
    </div>
  )
}

import React, { createContext, useContext, useState } from 'react'
import { api } from '../api/client.js'

const Ctx = createContext(null)

export function CopilotProvider({ children }) {
  const [isOpen, setOpen] = useState(false)
  const [mode, setMode] = useState('chat')
  const [messages, setMessages] = useState([])
  const [busy, setBusy] = useState(false)

  async function send(text, context = {}) {
    const userMsg = { role: 'user', content: text }
    const next = [...messages, userMsg]
    setMessages(next)
    setBusy(true)
    try {
      let result
      if (mode === 'agent') {
        result = await api.post('/api/v1/copilot/agent/', { goal: text, context })
      } else {
        result = await api.post('/api/v1/copilot/chat/', { messages: next, context })
      }
      setMessages([...next, { role: 'assistant', content: result.response_text || '(no response)', meta: result }])
    } catch (e) {
      setMessages([...next, { role: 'assistant', content: `Error: ${e.message}` }])
    } finally {
      setBusy(false)
    }
  }

  return (
    <Ctx.Provider value={{ isOpen, setOpen, mode, setMode, messages, busy, send }}>
      {children}
    </Ctx.Provider>
  )
}

export const useCopilot = () => useContext(Ctx)

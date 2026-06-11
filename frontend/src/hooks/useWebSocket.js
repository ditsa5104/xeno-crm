import { useEffect, useRef, useState } from 'react'
import { wsUrl } from '../api/client.js'

export function useWebSocket() {
  const [events, setEvents] = useState([])
  const wsRef = useRef(null)

  useEffect(() => {
    let ws
    let cancelled = false
    const connect = () => {
      ws = new WebSocket(wsUrl())
      wsRef.current = ws
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          setEvents((prev) => [msg, ...prev].slice(0, 50))
        } catch {}
      }
      ws.onclose = () => {
        if (!cancelled) setTimeout(connect, 3000)
      }
    }
    connect()
    return () => {
      cancelled = true
      if (ws) ws.close()
    }
  }, [])

  return { events }
}

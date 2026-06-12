const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let _token = localStorage.getItem('xeno_token') || ''

export function setToken(t) {
  _token = t || ''
}

export function getToken() {
  return _token
}

class ApiError extends Error {
  constructor(status, body) {
    super(typeof body === 'string' ? body : (body?.detail || JSON.stringify(body)))
    this.status = status
    this.body = body
  }
}

async function request(path, opts = {}) {
  const isFormData = opts.body instanceof FormData
  const headers = { ...(opts.headers || {}) }
  if (!isFormData) headers['Content-Type'] = headers['Content-Type'] || 'application/json'
  if (_token) headers['Authorization'] = `Token ${_token}`
  const resp = await fetch(`${BASE}${path}`, { ...opts, headers })
  if (!resp.ok) {
    let body
    try { body = await resp.json() } catch { body = await resp.text() }
    throw new ApiError(resp.status, body)
  }
  if (resp.status === 204) return null
  return resp.json()
}

export const api = {
  get: (p) => request(p),
  post: (p, body) => request(p, { method: 'POST', body: body instanceof FormData ? body : JSON.stringify(body) }),
  patch: (p, body) => request(p, { method: 'PATCH', body: JSON.stringify(body) }),
  del: (p) => request(p, { method: 'DELETE' }),
}

export const wsUrl = () => {
  const url = new URL(BASE)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  url.pathname = '/ws/events/'
  if (_token) url.searchParams.set('token', _token)
  return url.toString()
}

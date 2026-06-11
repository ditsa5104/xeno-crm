import React, { useState } from 'react'

export default function Import() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)

  async function upload() {
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    const token = localStorage.getItem('xeno_token') || ''
    const resp = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/customers/import-csv/`, {
      method: 'POST',
      headers: token ? { Authorization: `Token ${token}` } : {},
      body: fd,
    })
    setResult(await resp.json())
  }

  return (
    <div className="space-y-4 max-w-xl">
      <h1 className="text-2xl font-bold">Import customers</h1>
      <p className="text-sm text-gray-500">CSV columns: name, email, phone, city, channel_preference, gender</p>
      <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0])} />
      <button onClick={upload} disabled={!file} className="bg-indigo-600 text-white rounded px-3 py-1 disabled:opacity-50">Upload</button>
      {result && <pre className="text-xs bg-gray-100 p-2 rounded">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}

import React, { useState } from 'react'
import { Upload, FileText, CheckCircle2, Loader2 } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import { getToken } from '../api/client.js'

export default function Import() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [drag, setDrag] = useState(false)

  async function upload() {
    if (!file) return
    setBusy(true); setErr(''); setResult(null)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const token = getToken()
      const resp = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/customers/import-csv/`, {
        method: 'POST',
        headers: token ? { Authorization: `Token ${token}` } : {},
        body: fd,
      })
      if (!resp.ok) throw new Error(await resp.text())
      setResult(await resp.json())
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Import customers" subtitle="Upload a CSV to bulk-add or update customers." />

      <div className="card p-5">
        <div className="text-xs uppercase tracking-wide text-slate-500 font-medium mb-2">Required columns</div>
        <div className="flex gap-2 flex-wrap">
          {['name', 'email', 'phone', 'city', 'channel_preference', 'gender'].map((c) => (
            <code key={c} className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded">{c}</code>
          ))}
        </div>
      </div>

      <label
        onDragEnter={(e) => { e.preventDefault(); setDrag(true) }}
        onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault(); setDrag(false)
          const f = e.dataTransfer.files?.[0]
          if (f) setFile(f)
        }}
        className={`block card p-10 border-2 border-dashed cursor-pointer text-center transition ${
          drag ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
        }`}
      >
        <input type="file" accept=".csv" className="hidden" onChange={(e) => setFile(e.target.files?.[0])} />
        <div className="w-12 h-12 rounded-full bg-slate-100 grid place-items-center mx-auto mb-3 text-slate-500">
          {file ? <FileText className="w-5 h-5" /> : <Upload className="w-5 h-5" />}
        </div>
        {file ? (
          <>
            <div className="text-sm font-medium">{file.name}</div>
            <div className="text-xs text-slate-500 mt-1">{(file.size / 1024).toFixed(1)} KB</div>
          </>
        ) : (
          <>
            <div className="text-sm font-medium">Click to upload or drag and drop</div>
            <div className="text-xs text-slate-500 mt-1">CSV file up to 10 MB</div>
          </>
        )}
      </label>

      <div className="flex items-center gap-2">
        <button onClick={upload} disabled={!file || busy} className="btn-primary">
          {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          Upload
        </button>
        {file && <button onClick={() => { setFile(null); setResult(null); setErr('') }} className="btn-ghost">Clear</button>}
      </div>

      {err && <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2">{err}</div>}
      {result && (
        <div className="card p-4 border-emerald-200 bg-emerald-50/50 flex items-start gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5" />
          <div className="text-sm">
            <div className="font-medium text-emerald-900">Import complete</div>
            <div className="text-emerald-800 mt-1">Imported <strong>{result.imported}</strong> customer{result.imported === 1 ? '' : 's'}.</div>
          </div>
        </div>
      )}
    </div>
  )
}

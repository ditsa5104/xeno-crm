import React, { useState } from 'react'
import { Routes, Route, Link, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import Customers from './pages/Customers.jsx'
import Customer360 from './pages/Customer360.jsx'
import Segments from './pages/Segments.jsx'
import Campaigns from './pages/Campaigns.jsx'
import CampaignBuilder from './pages/CampaignBuilder.jsx'
import CampaignDetail from './pages/CampaignDetail.jsx'
import Analytics from './pages/Analytics.jsx'
import Import from './pages/Import.jsx'
import CopilotSidebar from './components/CopilotSidebar.jsx'

const NAV = [
  { to: '/', label: 'Dashboard' },
  { to: '/customers', label: 'Customers' },
  { to: '/segments', label: 'Segments' },
  { to: '/campaigns', label: 'Campaigns' },
  { to: '/analytics', label: 'Analytics' },
  { to: '/import', label: 'Import' },
]

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('xeno_token') || '')
  function saveToken(t) { localStorage.setItem('xeno_token', t); setToken(t) }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-56 bg-white border-r p-4 flex flex-col">
        <Link to="/" className="text-xl font-bold mb-6">✨ Xeno</Link>
        <nav className="space-y-1 flex-1">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === '/'}
              className={({ isActive }) => `block px-2 py-1 rounded text-sm ${isActive ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'}`}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="text-[10px] text-gray-400 mt-2">
          <input
            className="w-full border rounded px-1 py-0.5 mb-1"
            placeholder="API token"
            value={token}
            onChange={(e) => saveToken(e.target.value)}
          />
          (optional)
        </div>
      </aside>

      <main className="flex-1 p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/customers/:id" element={<Customer360 />} />
          <Route path="/segments" element={<Segments />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/campaigns/new" element={<CampaignBuilder />} />
          <Route path="/campaigns/:id" element={<CampaignDetail />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/import" element={<Import />} />
        </Routes>
      </main>

      <CopilotSidebar />
    </div>
  )
}

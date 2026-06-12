import React from 'react'
import { Routes, Route, NavLink, Link, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, Layers, Megaphone, BarChart3, Upload,
  Sparkles, LogOut, ChevronDown, BookOpen, PlayCircle,
} from 'lucide-react'
import Dashboard from './pages/Dashboard.jsx'
import Customers from './pages/Customers.jsx'
import Customer360 from './pages/Customer360.jsx'
import Segments from './pages/Segments.jsx'
import Campaigns from './pages/Campaigns.jsx'
import CampaignBuilder from './pages/CampaignBuilder.jsx'
import CampaignDetail from './pages/CampaignDetail.jsx'
import Analytics from './pages/Analytics.jsx'
import Import from './pages/Import.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import CopilotSidebar from './components/CopilotSidebar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import OnboardingDemo from './components/OnboardingDemo.jsx'
import { useAuth } from './contexts/AuthContext.jsx'
import { useCopilot } from './contexts/CopilotContext.jsx'
import { useOnboarding } from './contexts/OnboardingContext.jsx'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/customers', label: 'Customers', icon: Users },
  { to: '/segments', label: 'Segments', icon: Layers },
  { to: '/campaigns', label: 'Campaigns', icon: Megaphone },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/import', label: 'Import', icon: Upload },
]

function Shell() {
  const { user, logout } = useAuth()
  const { setOpen } = useCopilot()
  const { start } = useOnboarding()
  const [menu, setMenu] = React.useState(false)
  const nav = useNavigate()

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col">
        <Link to="/" className="px-5 py-5 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 grid place-items-center text-white">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="text-lg font-bold tracking-tight">Xeno</span>
        </Link>

        <nav className="px-3 space-y-1 flex-1 mt-2">
          {NAV.map((n) => {
            const Icon = n.icon
            return (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {n.label}
              </NavLink>
            )
          })}
        </nav>

        <div className="p-3 space-y-2">
          <button
            onClick={() => setOpen(true)}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-sm"
          >
            <Sparkles className="w-4 h-4" /> Copilot
          </button>
          <a
            href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/docs/`}
            target="_blank"
            rel="noreferrer"
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition"
          >
            <BookOpen className="w-4 h-4" /> API docs
          </a>
          <button
            onClick={start}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition"
          >
            <PlayCircle className="w-4 h-4" /> Replay Demo
          </button>
        </div>

        <div className="border-t border-slate-200 p-3 relative">
          <button
            onClick={() => setMenu((m) => !m)}
            className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-100 transition"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 grid place-items-center text-white text-xs font-semibold">
              {(user?.name || user?.username || 'U').slice(0, 1).toUpperCase()}
            </div>
            <div className="flex-1 text-left min-w-0">
              <div className="text-sm font-medium text-slate-900 truncate">{user?.name || user?.username}</div>
              <div className="text-xs text-slate-500 truncate">{user?.email}</div>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>
          {menu && (
            <div className="absolute bottom-16 left-3 right-3 bg-white border border-slate-200 rounded-lg shadow-lg overflow-hidden">
              <button
                onClick={async () => { await logout(); nav('/login') }}
                className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" /> Sign out
              </button>
            </div>
          )}
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-8 py-8">
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
        </div>
      </main>

      <CopilotSidebar />
      <OnboardingDemo />
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/*" element={<ProtectedRoute><Shell /></ProtectedRoute>} />
    </Routes>
  )
}

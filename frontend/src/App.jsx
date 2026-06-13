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
import Logo from './components/Logo.jsx'
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
    <div className="min-h-screen flex">
      <aside className="w-64 shrink-0 flex flex-col sticky top-0 h-screen border-r border-white/5 bg-slate-950/60 backdrop-blur-xl">
        <Link to="/" className="px-5 py-5 flex items-center gap-2.5 group">
          <Logo size="md" tone="light" showBadge />
        </Link>

        <nav className="px-3 space-y-0.5 flex-1 mt-1">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 px-3 mb-1.5">Workspace</div>
          {NAV.map((n) => {
            const Icon = n.icon
            return (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  `group relative flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-white/10 text-white shadow-soft'
                      : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && (
                      <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-1 rounded-r-full bg-gradient-to-b from-indigo-400 to-pink-400" />
                    )}
                    <Icon className={`w-[18px] h-[18px] transition-transform ${isActive ? 'text-brand-300' : 'group-hover:scale-110'}`} />
                    {n.label}
                  </>
                )}
              </NavLink>
            )
          })}
        </nav>

        <div className="p-3 space-y-2">
          <button
            onClick={() => setOpen(true)}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm font-semibold text-white btn-gradient !justify-start"
          >
            <Sparkles className="w-4 h-4" /> Ask Copilot
          </button>
          <div className="flex gap-2">
            <a
              href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/docs/`}
              target="_blank"
              rel="noreferrer"
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg text-xs font-medium text-slate-400 hover:bg-white/5 hover:text-white transition"
            >
              <BookOpen className="w-3.5 h-3.5" /> API
            </a>
            <button
              onClick={start}
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-2 rounded-lg text-xs font-medium text-slate-400 hover:bg-white/5 hover:text-white transition"
            >
              <PlayCircle className="w-3.5 h-3.5" /> Demo
            </button>
          </div>
        </div>

        <div className="border-t border-white/5 p-3 relative">
          <button
            onClick={() => setMenu((m) => !m)}
            className="w-full flex items-center gap-2.5 px-2 py-1.5 rounded-xl hover:bg-white/5 transition"
          >
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 grid place-items-center text-white text-xs font-bold shadow-soft">
              {(user?.name || user?.username || 'U').slice(0, 1).toUpperCase()}
            </div>
            <div className="flex-1 text-left min-w-0">
              <div className="text-sm font-semibold text-white truncate">{user?.name || user?.username}</div>
              <div className="text-xs text-slate-500 truncate">{user?.email}</div>
            </div>
            <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${menu ? 'rotate-180' : ''}`} />
          </button>
          {menu && (
            <div className="absolute bottom-16 left-3 right-3 bg-slate-900 border border-white/10 rounded-xl shadow-lift overflow-hidden animate-scale-in origin-bottom">
              <button
                onClick={async () => { await logout(); nav('/login') }}
                className="w-full text-left px-3 py-2.5 text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" /> Sign out
              </button>
            </div>
          )}
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto px-8 py-8 animate-fade-up">
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

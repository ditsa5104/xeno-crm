import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, ArrowRight, ArrowLeft, X } from 'lucide-react'
import { useOnboarding } from '../contexts/OnboardingContext.jsx'

// Step definitions per the Mini CRM spec (steps 0–5). Each step optionally
// navigates to a route and shows a tooltip card.
const STEPS = [
  {
    kind: 'welcome',
    title: 'Welcome to Plume',
    body: 'Let us show you how it works — a quick, clickable tour using two ready-made campaigns.',
    route: '/',
  },
  {
    kind: 'tooltip',
    title: 'Your performance overview',
    body: 'This is your campaign performance overview. Everything your campaigns do shows up here in real time — total customers, messages, delivered and open rates.',
    route: '/',
  },
  {
    kind: 'tooltip',
    title: 'Campaign 1 — Birthday 🎂',
    body: 'This campaign automatically messages customers on their birthday with a personalised discount, celebrating our 2-year anniversary too.',
    route: '/campaigns',
  },
  {
    kind: 'tooltip',
    title: "Campaign 2 — Skirts Launch 👗",
    body: 'This campaign targets only customers who have bought skirts before — hyper-personalised, using the "Skirt Buyers — Last 12 Months" segment.',
    route: '/campaigns',
  },
  {
    kind: 'tooltip',
    title: 'Build your own segments',
    body: 'Want to reach a specific group? Build a segment using customer behaviour and attributes — like All Customers, Skirt Buyers, Birthday This Month, or High Spenders.',
    route: '/segments',
  },
  {
    kind: 'complete',
    title: "That's Plume in action",
    body: "You're all set! Explore your dashboard, customers, segments, and campaigns whenever you're ready.",
    route: '/',
  },
]

export default function OnboardingDemo() {
  const { active, step, next, prev, finish } = useOnboarding()
  const nav = useNavigate()
  const current = STEPS[step]

  // Drive navigation as the step changes.
  React.useEffect(() => {
    if (active && current?.route) nav(current.route)
  }, [active, step]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!active || !current) return null

  const isFirst = step === 0
  const isLast = step === STEPS.length - 1

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      {/* Soft overlay */}
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px] onboarding-pulse" />

      <div className="relative w-full max-w-md rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
        {/* Gentle gradient header */}
        <div className="h-24 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 relative">
          <div className="absolute inset-0 onboarding-gradient-pulse opacity-70" />
          <button
            onClick={finish}
            className="absolute top-3 right-3 text-white/80 hover:text-white"
            aria-label="Skip demo"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="absolute -bottom-6 left-6 w-12 h-12 rounded-2xl bg-white shadow-md grid place-items-center">
            <Sparkles className="w-6 h-6 text-purple-600" />
          </div>
        </div>

        <div className="p-6 pt-9">
          <div className="text-xs font-semibold uppercase tracking-wide text-purple-500 mb-1">
            {isFirst || isLast ? 'Interactive demo' : `Step ${step} of ${STEPS.length - 2}`}
          </div>
          <h2 className="text-xl font-bold text-slate-900">{current.title}</h2>
          <p className="text-sm text-slate-600 mt-2 leading-relaxed">{current.body}</p>

          <div className="flex items-center justify-between gap-2 mt-6">
            {current.kind === 'welcome' ? (
              <>
                <button onClick={finish} className="btn-ghost">Skip to Dashboard</button>
                <button onClick={next} className="btn-gradient !rounded-full !px-5">
                  Start Interactive Demo <ArrowRight className="w-4 h-4" />
                </button>
              </>
            ) : current.kind === 'complete' ? (
              <button onClick={finish} className="btn-gradient !rounded-full !px-5 w-full justify-center">
                Go to Dashboard <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <>
                <button onClick={prev} className="btn-ghost" disabled={isFirst}>
                  <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <button onClick={next} className="btn-gradient !rounded-full !px-5">
                  Next <ArrowRight className="w-4 h-4" />
                </button>
              </>
            )}
          </div>

          {/* Progress dots */}
          <div className="flex justify-center gap-1.5 mt-5">
            {STEPS.map((_, i) => (
              <span
                key={i}
                className={`h-1.5 rounded-full transition-all ${
                  i === step ? 'w-5 bg-purple-500' : 'w-1.5 bg-slate-200'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

import React from 'react'

const STORAGE_KEY = 'xeno_demo_seen'
const OnboardingContext = React.createContext(null)

export function OnboardingProvider({ children }) {
  // active: whether the demo overlay is showing. step: 0–5.
  const [active, setActive] = React.useState(false)
  const [step, setStep] = React.useState(0)

  // Auto-start on first ever load.
  React.useEffect(() => {
    const seen = localStorage.getItem(STORAGE_KEY)
    if (!seen) {
      setActive(true)
      setStep(0)
    }
  }, [])

  const start = React.useCallback(() => {
    setStep(0)
    setActive(true)
  }, [])

  const finish = React.useCallback(() => {
    localStorage.setItem(STORAGE_KEY, 'true')
    setActive(false)
    setStep(0)
  }, [])

  const next = React.useCallback(() => setStep((s) => s + 1), [])
  const prev = React.useCallback(() => setStep((s) => Math.max(0, s - 1)), [])

  const value = { active, step, start, finish, next, prev, setStep }
  return <OnboardingContext.Provider value={value}>{children}</OnboardingContext.Provider>
}

export function useOnboarding() {
  const ctx = React.useContext(OnboardingContext)
  if (!ctx) throw new Error('useOnboarding must be used within OnboardingProvider')
  return ctx
}

import { createContext, useContext, type ReactNode } from 'react'
import { useLeads } from '@/hooks/useLeads'
import { useSettings } from '@/hooks/useSettings'

type LeadsAPI = ReturnType<typeof useLeads>
type SettingsAPI = ReturnType<typeof useSettings>

const LeadsCtx = createContext<LeadsAPI | null>(null)
const SettingsCtx = createContext<SettingsAPI | null>(null)

export function AppStoreProvider({ children }: { children: ReactNode }) {
  const leads = useLeads()
  const settings = useSettings()
  return (
    <LeadsCtx.Provider value={leads}>
      <SettingsCtx.Provider value={settings}>{children}</SettingsCtx.Provider>
    </LeadsCtx.Provider>
  )
}

export function useLeadsStore(): LeadsAPI {
  const ctx = useContext(LeadsCtx)
  if (!ctx) throw new Error('useLeadsStore must be used within AppStoreProvider')
  return ctx
}

export function useSettingsStore(): SettingsAPI {
  const ctx = useContext(SettingsCtx)
  if (!ctx) throw new Error('useSettingsStore must be used within AppStoreProvider')
  return ctx
}

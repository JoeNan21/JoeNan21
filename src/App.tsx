import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { BriefPage } from '@/pages/Brief'
import { PipelinePage } from '@/pages/Pipeline'
import { ComposerPage } from '@/pages/Composer'
import { ForecastPage } from '@/pages/Forecast'
import { ToolsPage } from '@/pages/Tools'
import { SettingsPage } from '@/pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<BriefPage />} />
        <Route path="pipeline" element={<PipelinePage />} />
        <Route path="composer" element={<ComposerPage />} />
        <Route path="forecast" element={<ForecastPage />} />
        <Route path="tools" element={<ToolsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

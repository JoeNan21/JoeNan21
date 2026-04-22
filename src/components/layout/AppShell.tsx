import { NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  ClipboardList,
  KanbanSquare,
  Mail,
  LineChart,
  Wrench,
  Settings as SettingsIcon,
} from 'lucide-react'
import { cn } from '@/lib/cn'

const NAV = [
  { to: '/', label: 'Brief', icon: ClipboardList, end: true },
  { to: '/pipeline', label: 'Pipeline', icon: KanbanSquare },
  { to: '/composer', label: 'Draft', icon: Mail },
  { to: '/forecast', label: 'Forecast', icon: LineChart },
  { to: '/tools', label: 'Tools', icon: Wrench },
]

export function AppShell() {
  const location = useLocation()
  const activeTitle = NAV.find((n) => (n.end ? location.pathname === n.to : location.pathname.startsWith(n.to)))?.label ?? 'CAOS'

  return (
    <div className="min-h-screen flex">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-[240px] border-r border-line bg-surface flex-shrink-0 sticky top-0 h-screen">
        <div className="px-5 py-5 border-b border-line">
          <div className="text-[10px] tracking-[0.2em] uppercase text-gold font-medium">Sorrento</div>
          <div className="text-ink font-semibold text-lg mt-1 leading-tight">CAOS</div>
          <div className="text-muted text-[11px] mt-0.5">Revenue OS</div>
        </div>
        <nav className="flex-1 py-3">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-5 py-3 text-sm transition-colors border-l-2',
                  isActive
                    ? 'text-gold border-gold bg-gold/5'
                    : 'text-muted border-transparent hover:text-ink',
                )
              }
            >
              <n.icon size={18} />
              <span>{n.label}</span>
            </NavLink>
          ))}
        </nav>
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-5 py-4 text-sm border-t border-line transition-colors',
              isActive ? 'text-gold' : 'text-muted hover:text-ink',
            )
          }
        >
          <SettingsIcon size={18} />
          <span>Settings</span>
        </NavLink>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 border-b border-line bg-surface sticky top-0 z-30">
          <div>
            <div className="text-[9px] tracking-[0.2em] uppercase text-gold font-medium">CAOS</div>
            <div className="text-ink font-semibold text-base leading-tight">{activeTitle}</div>
          </div>
          <NavLink
            to="/settings"
            className="btn-icon"
            aria-label="Settings"
          >
            <SettingsIcon size={18} />
          </NavLink>
        </header>

        <div className="flex-1 pb-[72px] md:pb-0">
          <Outlet />
        </div>

        {/* Mobile bottom nav */}
        <nav
          className="md:hidden fixed bottom-0 inset-x-0 z-50 bg-surface border-t border-line flex"
          style={{ paddingBottom: 'env(safe-area-inset-bottom)' }}
        >
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                cn(
                  'flex-1 flex flex-col items-center justify-center gap-1 py-2.5 text-[10px] tracking-wide uppercase transition-colors',
                  isActive ? 'text-gold' : 'text-muted',
                )
              }
            >
              <n.icon size={20} />
              <span>{n.label}</span>
            </NavLink>
          ))}
        </nav>
      </main>
    </div>
  )
}

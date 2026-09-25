import { NavLink } from 'react-router-dom'
import { LayoutGrid, ScanSearch, Network, History, Activity } from 'lucide-react'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutGrid, end: true },
  { to: '/individual', label: 'Individual Verification', icon: ScanSearch },
  { to: '/multi', label: 'Multi-Document Verification', icon: Network },
  { to: '/history', label: 'History / Cases', icon: History },
  { to: '/system-status', label: 'System Status', icon: Activity }
]

export default function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 border-r border-border bg-white md:block">
      <nav className="sticky top-16 flex flex-col gap-1 p-4">
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? 'bg-brand-50 text-brand-700 font-medium'
                  : 'text-muted hover:bg-ink/[0.03] hover:text-ink'
              }`
            }
          >
            <Icon size={17} strokeWidth={2} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

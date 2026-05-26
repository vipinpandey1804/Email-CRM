import { NavLink, Outlet } from 'react-router-dom'
import { Building2, Mail } from 'lucide-react'
import { cn } from '@/lib/utils'

const settingsNav = [
  { to: '/settings', label: 'Organization', icon: Building2, end: true },
  { to: '/settings/smtp', label: 'SMTP Setup', icon: Mail, end: false },
]

export default function SettingsLayout() {
  return (
    <div className="flex gap-6">
      {/* Settings sidebar */}
      <div className="w-48 flex-shrink-0">
        <h2 className="text-lg font-bold text-foreground mb-4">Settings</h2>
        <nav className="space-y-1">
          {settingsNav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                )
              }
            >
              <Icon size={15} />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <Outlet />
      </div>
    </div>
  )
}

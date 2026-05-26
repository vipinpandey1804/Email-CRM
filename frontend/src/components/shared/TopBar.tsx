import { useAuthStore } from '@/features/auth/useAuthStore'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'

export default function TopBar() {
  const { user, orgSlug, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem('refresh_token')
    try {
      await api.post('/auth/logout', { refresh: refreshToken })
    } catch {
      /* ignore */
    }
    logout()
    navigate('/login')
  }

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6 fixed top-0 right-0 left-60 z-10">
      <div />
      <div className="flex items-center gap-4">
        {orgSlug && (
          <span className="text-xs text-muted-foreground bg-accent px-2 py-1 rounded font-mono">
            {orgSlug}
          </span>
        )}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-medium text-sm">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <button
            onClick={handleLogout}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

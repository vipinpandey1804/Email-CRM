import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from './useAuthStore'
import api from '@/lib/api'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { setTokens, setUser, setOrgSlug } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/auth/token', { email, password })
      setTokens(data.access, data.refresh)
      const { data: userData } = await api.get('/auth/me')
      setUser(userData)
      // Fetch user's first org
      const { data: orgs } = await api.get('/orgs/')
      if (orgs.length > 0) setOrgSlug(orgs[0].slug)
      navigate('/campaigns')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = () => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID
    const redirectUri = `${window.location.origin}/auth/google/callback`
    const scope = 'openid email profile'
    const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=id_token&scope=${scope}&nonce=${Math.random()}`
    window.location.href = url
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 rounded-xl border border-border bg-card shadow-xl">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center text-white font-bold text-xl">
              M
            </div>
            <span className="text-xl font-bold text-foreground">Maven Emailer</span>
          </div>
          <p className="text-muted-foreground text-sm">Enterprise Email Campaign Platform</p>
        </div>

        {/* Google OAuth */}
        <button
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-border rounded-lg text-foreground hover:bg-accent transition-colors mb-6"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          Continue with Google
        </button>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center text-xs text-muted-foreground bg-card px-2">
            or sign in with email
          </div>
        </div>

        {/* Email/Password Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="you@company.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="••••••••"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}

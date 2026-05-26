import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from './useAuthStore'
import api from '@/lib/api'

/**
 * Handles the Google OAuth implicit-flow redirect. Google returns the
 * id_token in the URL fragment (#id_token=...). We exchange it with the
 * backend POST /auth/google endpoint for our own JWT pair.
 */
export default function GoogleOAuthCallback() {
  const navigate = useNavigate()
  const { setTokens, setUser, setOrgSlug } = useAuthStore()
  const [error, setError] = useState('')

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1))
    const idToken = params.get('id_token')

    if (!idToken) {
      setError('No Google credentials returned. Please try again.')
      return
    }

    ;(async () => {
      try {
        const { data } = await api.post('/auth/google', { id_token: idToken })
        setTokens(data.access, data.refresh)
        const { data: userData } = await api.get('/auth/me')
        setUser(userData)
        const { data: orgs } = await api.get('/orgs/')
        if (orgs.length > 0) setOrgSlug(orgs[0].slug)
        navigate('/campaigns', { replace: true })
      } catch {
        setError('Google sign-in failed. Please try again.')
      }
    })()
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      {error ? (
        <div className="text-center">
          <p className="text-destructive text-sm mb-4">{error}</p>
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm"
          >
            Back to Login
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" />
          Completing Google sign-in...
        </div>
      )}
    </div>
  )
}

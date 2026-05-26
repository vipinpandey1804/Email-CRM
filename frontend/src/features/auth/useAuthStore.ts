import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  orgSlug: string | null
  setTokens: (access: string, refresh: string) => void
  setUser: (user: User) => void
  setOrgSlug: (slug: string) => void
  logout: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      orgSlug: null,
      setTokens: (access, refresh) => {
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        set({ accessToken: access, refreshToken: refresh })
      },
      setUser: (user) => set({ user }),
      setOrgSlug: (slug) => {
        localStorage.setItem('org_slug', slug)
        set({ orgSlug: slug })
      },
      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('org_slug')
        set({ user: null, accessToken: null, refreshToken: null, orgSlug: null })
      },
      isAuthenticated: () => !!get().accessToken,
    }),
    {
      name: 'auth-storage',
      partialize: (s) => ({
        accessToken: s.accessToken,
        refreshToken: s.refreshToken,
        orgSlug: s.orgSlug,
        user: s.user,
      }),
    }
  )
)

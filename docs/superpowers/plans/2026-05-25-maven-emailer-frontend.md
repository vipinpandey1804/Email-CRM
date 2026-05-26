# Maven Technosoft Emailer — Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the React+Vite frontend for the Maven Technosoft Enterprise Emailer — JWT+Google auth, GrapesJS email editor with MJML browser-side compilation, campaign management dashboard, AI panel with SSE streaming, and settings pages.

**Architecture:** Feature-sliced directory structure; Zustand for client state (auth, editor, AI); TanStack Query for all server state; GrapesJS+grapesjs-mjml for the email canvas with client-side MJML→HTML compilation; useSSEStream hook consumes Django async SSE; shadcn/ui + Tailwind for the design system.

**Tech Stack:** React 18, Vite 5, TypeScript 5, React Router 6, Zustand 4, TanStack Query 5, Axios, GrapesJS 0.21, grapesjs-mjml, mjml-browser, Tailwind CSS 3, shadcn/ui, @radix-ui

**Prerequisite:** Backend plan complete and running on `http://localhost:8000`.

---

## File Map

```
frontend/
├── src/
│   ├── app/
│   │   ├── router.tsx         # All routes + ProtectedRoute wrapper
│   │   └── queryClient.ts     # TanStack QueryClient config
│   ├── features/
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── GoogleOAuthCallback.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── useAuthStore.ts
│   │   ├── campaigns/
│   │   │   ├── CampaignList.tsx
│   │   │   ├── CampaignDetail.tsx
│   │   │   ├── CreateCampaignWizard.tsx
│   │   │   ├── ScheduleSendModal.tsx
│   │   │   └── useCampaigns.ts    # TanStack Query hooks
│   │   ├── editor/
│   │   │   ├── EditorPage.tsx     # Full-screen layout
│   │   │   ├── GrapesEditor.tsx   # GrapesJS mount + save
│   │   │   ├── SubjectLineBar.tsx
│   │   │   ├── CTAPanel.tsx
│   │   │   ├── PreviewToggle.tsx
│   │   │   └── useEditorStore.ts
│   │   ├── templates/
│   │   │   ├── TemplateLibrary.tsx
│   │   │   ├── TemplateCard.tsx
│   │   │   └── useTemplates.ts
│   │   ├── ai/
│   │   │   ├── AIPanel.tsx
│   │   │   ├── SubjectSuggestions.tsx
│   │   │   ├── CopyOptimizer.tsx
│   │   │   ├── SpamChecker.tsx
│   │   │   ├── CTASuggestions.tsx
│   │   │   ├── useSSEStream.ts
│   │   │   └── useAIStore.ts
│   │   └── settings/
│   │       ├── SettingsLayout.tsx
│   │       ├── SMTPSetup.tsx
│   │       ├── OrgSettings.tsx
│   │       └── UserManagement.tsx
│   ├── components/
│   │   ├── ui/                # shadcn/ui components (Button, Input, etc.)
│   │   └── shared/
│   │       ├── AppShell.tsx   # Sidebar + TopBar wrapper
│   │       ├── Sidebar.tsx
│   │       └── TopBar.tsx
│   ├── lib/
│   │   ├── api.ts             # Axios instance + JWT interceptors
│   │   └── utils.ts
│   └── types/
│       └── index.ts           # All shared TypeScript interfaces
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

---

## Task 1: Scaffold React+Vite Project

**Files:**
- Create: `frontend/` (all structure)
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/tsconfig.json`

- [ ] **Step 1: Create Vite project**

```bash
cd "E:/career247/New folder (2)/project 1"
npm create vite@latest frontend -- --template react-ts
cd frontend
```

- [ ] **Step 2: Install all dependencies**

```bash
npm install \
  react-router-dom \
  zustand \
  @tanstack/react-query \
  axios \
  grapesjs \
  grapesjs-mjml \
  @types/grapesjs \
  tailwindcss postcss autoprefixer \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-select \
  @radix-ui/react-toast \
  @radix-ui/react-tabs \
  @radix-ui/react-label \
  @radix-ui/react-slot \
  class-variance-authority \
  clsx \
  tailwind-merge \
  lucide-react \
  date-fns \
  @google/identity

npm install -D \
  @types/node \
  @vitejs/plugin-react
```

- [ ] **Step 3: Initialize Tailwind**

```bash
npx tailwindcss init -p
```

- [ ] **Step 4: Update `frontend/tailwind.config.ts`**

```typescript
import type { Config } from 'tailwindcss'

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
} satisfies Config
```

- [ ] **Step 5: Update `frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 6: Create `frontend/src/types/index.ts`**

```typescript
export interface User {
  id: string
  email: string
  full_name: string
  is_staff: boolean
}

export interface Organization {
  id: number
  name: string
  slug: string
  is_active: boolean
  plan: string
  logo_url: string
}

export interface EmailTemplate {
  id: string
  name: string
  category: string
  thumbnail_url: string
  is_system: boolean
  gjs_components: Record<string, unknown>
  gjs_styles: Record<string, unknown>
  mjml_source: string
  html_output: string
  updated_at: string
}

export interface Campaign {
  id: string
  name: string
  subject_line: string
  preview_text: string
  from_name: string
  from_email: string
  reply_to: string
  tags: string[]
  status: 'draft' | 'scheduled' | 'sending' | 'sent' | 'failed'
  scheduled_at: string | null
  sent_at: string | null
  created_at: string
}

export interface CampaignRecipient {
  id: string
  email: string
  name: string
  status: 'queued' | 'sent' | 'failed'
  sent_at: string | null
  error_message: string
}

export interface AIJob {
  id: string
  job_type: string
  status: 'pending' | 'running' | 'done' | 'failed'
  input_data: Record<string, unknown>
  output_data: Record<string, unknown> | null
  created_at: string
  completed_at: string | null
}

export interface SMTPConfig {
  host: string
  port: number
  username: string
  use_tls: boolean
  use_ssl: boolean
  is_verified: boolean
}
```

- [ ] **Step 7: Create `frontend/src/lib/api.ts`**

```typescript
import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Inject JWT access token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/token/refresh', { refresh: refreshToken })
          localStorage.setItem('access_token', data.access)
          localStorage.setItem('refresh_token', data.refresh)
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 8: Create `frontend/src/app/queryClient.ts`**

```typescript
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
```

- [ ] **Step 9: Create CSS variables in `frontend/src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 222 47% 8%;
    --foreground: 210 40% 95%;
    --card: 222 47% 11%;
    --card-foreground: 210 40% 95%;
    --primary: 348 83% 47%;
    --primary-foreground: 0 0% 100%;
    --secondary: 222 47% 15%;
    --secondary-foreground: 210 40% 95%;
    --muted: 222 47% 15%;
    --muted-foreground: 215 20% 55%;
    --accent: 222 47% 18%;
    --accent-foreground: 210 40% 95%;
    --destructive: 0 72% 51%;
    --destructive-foreground: 0 0% 100%;
    --border: 222 47% 18%;
    --input: 222 47% 18%;
    --ring: 348 83% 47%;
    --radius: 0.5rem;
  }
}

body {
  @apply bg-background text-foreground;
  font-family: 'Inter', system-ui, sans-serif;
}

/* GrapesJS editor override */
.gjs-editor {
  font-family: 'Inter', system-ui, sans-serif !important;
}
```

- [ ] **Step 10: Create `frontend/src/lib/utils.ts`**

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getOrgSlug(): string {
  return localStorage.getItem('org_slug') || ''
}
```

- [ ] **Step 11: Verify dev server starts**

```bash
npm run dev
```

Expected: Vite server starts at `http://localhost:5173`. Browser shows default React page.

- [ ] **Step 12: Commit**

```bash
cd "E:/career247/New folder (2)/project 1"
git add frontend/
git commit -m "chore: scaffold React+Vite frontend with Tailwind + TanStack + Zustand"
```

---

## Task 2: Auth Store + Login Page

**Files:**
- Create: `frontend/src/features/auth/useAuthStore.ts`
- Create: `frontend/src/features/auth/LoginPage.tsx`
- Create: `frontend/src/features/auth/ProtectedRoute.tsx`

- [ ] **Step 1: Create `frontend/src/features/auth/useAuthStore.ts`**

```typescript
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
    { name: 'auth-storage', partialize: (s) => ({ accessToken: s.accessToken, refreshToken: s.refreshToken, orgSlug: s.orgSlug, user: s.user }) }
  )
)
```

- [ ] **Step 2: Create `frontend/src/features/auth/LoginPage.tsx`**

```typescript
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
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center text-white font-bold text-xl">M</div>
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
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </button>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center text-xs text-muted-foreground bg-card px-2">or sign in with email</div>
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
```

- [ ] **Step 3: Create `frontend/src/features/auth/ProtectedRoute.tsx`**

```typescript
import { Navigate } from 'react-router-dom'
import { useAuthStore } from './useAuthStore'

interface Props {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: Props) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/auth/
git commit -m "feat: auth store, login page, protected route"
```

---

## Task 3: App Shell + Routing

**Files:**
- Create: `frontend/src/components/shared/AppShell.tsx`
- Create: `frontend/src/components/shared/Sidebar.tsx`
- Create: `frontend/src/components/shared/TopBar.tsx`
- Create: `frontend/src/app/router.tsx`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Create `frontend/src/components/shared/Sidebar.tsx`**

```typescript
import { NavLink } from 'react-router-dom'
import { Mail, LayoutTemplate, Settings, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/campaigns', icon: Mail, label: 'Campaigns' },
  { to: '/templates', icon: LayoutTemplate, label: 'Templates' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 h-screen bg-card border-r border-border flex flex-col fixed left-0 top-0">
      {/* Logo */}
      <div className="p-5 border-b border-border flex items-center gap-3">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">M</div>
        <div>
          <p className="font-bold text-foreground text-sm">Maven Emailer</p>
          <p className="text-muted-foreground text-xs">Enterprise Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground hover:bg-accent hover:text-foreground'
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/shared/TopBar.tsx`**

```typescript
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
    } catch {}
    logout()
    navigate('/login')
  }

  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6 fixed top-0 right-0 left-60 z-10">
      <div />
      <div className="flex items-center gap-4">
        <span className="text-xs text-muted-foreground bg-accent px-2 py-1 rounded font-mono">{orgSlug}</span>
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
```

- [ ] **Step 3: Create `frontend/src/components/shared/AppShell.tsx`**

```typescript
import Sidebar from './Sidebar'
import TopBar from './TopBar'

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <TopBar />
      <main className="ml-60 pt-14 p-6 min-h-screen">
        {children}
      </main>
    </div>
  )
}
```

- [ ] **Step 4: Create `frontend/src/app/router.tsx`**

```typescript
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import ProtectedRoute from '@/features/auth/ProtectedRoute'
import LoginPage from '@/features/auth/LoginPage'
import AppShell from '@/components/shared/AppShell'
import CampaignList from '@/features/campaigns/CampaignList'
import CampaignDetail from '@/features/campaigns/CampaignDetail'
import CreateCampaignWizard from '@/features/campaigns/CreateCampaignWizard'
import TemplateLibrary from '@/features/templates/TemplateLibrary'
import EditorPage from '@/features/editor/EditorPage'
import SettingsLayout from '@/features/settings/SettingsLayout'
import SMTPSetup from '@/features/settings/SMTPSetup'
import OrgSettings from '@/features/settings/OrgSettings'

const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell>
          <Navigate to="/campaigns" replace />
        </AppShell>
      </ProtectedRoute>
    ),
  },
  {
    path: '/campaigns',
    element: (
      <ProtectedRoute>
        <AppShell><CampaignList /></AppShell>
      </ProtectedRoute>
    ),
  },
  {
    path: '/campaigns/new',
    element: (
      <ProtectedRoute>
        <AppShell><CreateCampaignWizard /></AppShell>
      </ProtectedRoute>
    ),
  },
  {
    path: '/campaigns/:id',
    element: (
      <ProtectedRoute>
        <AppShell><CampaignDetail /></AppShell>
      </ProtectedRoute>
    ),
  },
  {
    path: '/templates',
    element: (
      <ProtectedRoute>
        <AppShell><TemplateLibrary /></AppShell>
      </ProtectedRoute>
    ),
  },
  {
    path: '/editor/:templateId',
    element: (
      <ProtectedRoute>
        <EditorPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute>
        <AppShell><SettingsLayout /></AppShell>
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <OrgSettings /> },
      { path: 'smtp', element: <SMTPSetup /> },
    ],
  },
])

export default function AppRouter() {
  return <RouterProvider router={router} />
}
```

- [ ] **Step 5: Update `frontend/src/main.tsx`**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from './app/queryClient'
import AppRouter from './app/router'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AppRouter />
    </QueryClientProvider>
  </React.StrictMode>
)
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat: app shell, sidebar, topbar, routing"
```

---

## Task 4: Campaigns Feature

**Files:**
- Create: `frontend/src/features/campaigns/useCampaigns.ts`
- Create: `frontend/src/features/campaigns/CampaignList.tsx`
- Create: `frontend/src/features/campaigns/CampaignDetail.tsx`
- Create: `frontend/src/features/campaigns/CreateCampaignWizard.tsx`

- [ ] **Step 1: Create `frontend/src/features/campaigns/useCampaigns.ts`**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { Campaign } from '@/types'

export function useCampaigns(status?: string) {
  const orgSlug = getOrgSlug()
  return useQuery<Campaign[]>({
    queryKey: ['campaigns', orgSlug, status],
    queryFn: async () => {
      const params = new URLSearchParams({ org_slug: orgSlug })
      if (status) params.append('status', status)
      const { data } = await api.get(`/campaigns/?${params}`)
      return data
    },
    enabled: !!orgSlug,
  })
}

export function useCampaign(id: string) {
  const orgSlug = getOrgSlug()
  return useQuery<Campaign>({
    queryKey: ['campaign', id],
    queryFn: async () => {
      const { data } = await api.get(`/campaigns/${id}?org_slug=${orgSlug}`)
      return data
    },
  })
}

export function useCreateCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: Partial<Campaign>) =>
      api.post(`/campaigns/?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useUpdateCampaign(id: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: Partial<Campaign>) =>
      api.patch(`/campaigns/${id}?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['campaigns'] })
      qc.invalidateQueries({ queryKey: ['campaign', id] })
    },
  })
}

export function useDeleteCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (id: string) =>
      api.delete(`/campaigns/${id}?org_slug=${orgSlug}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useSendCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (id: string) =>
      api.post(`/campaigns/${id}/send-now?org_slug=${orgSlug}`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useScheduleCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: ({ id, scheduled_at }: { id: string; scheduled_at: string }) =>
      api.post(`/campaigns/${id}/schedule?org_slug=${orgSlug}`, { scheduled_at }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}
```

- [ ] **Step 2: Create `frontend/src/features/campaigns/CampaignList.tsx`**

```typescript
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Send, Clock, CheckCircle, XCircle, FileText } from 'lucide-react'
import { useCampaigns, useDeleteCampaign } from './useCampaigns'
import { cn } from '@/lib/utils'

const statusConfig = {
  draft: { label: 'Draft', icon: FileText, color: 'text-muted-foreground' },
  scheduled: { label: 'Scheduled', icon: Clock, color: 'text-yellow-400' },
  sending: { label: 'Sending', icon: Send, color: 'text-blue-400' },
  sent: { label: 'Sent', icon: CheckCircle, color: 'text-green-400' },
  failed: { label: 'Failed', icon: XCircle, color: 'text-destructive' },
}

export default function CampaignList() {
  const { data: campaigns, isLoading } = useCampaigns()
  const deleteMutation = useDeleteCampaign()
  const navigate = useNavigate()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Campaigns</h1>
          <p className="text-muted-foreground text-sm mt-1">{campaigns?.length || 0} total campaigns</p>
        </div>
        <Link
          to="/campaigns/new"
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          <Plus size={16} />
          New Campaign
        </Link>
      </div>

      {/* Table */}
      {!campaigns?.length ? (
        <div className="text-center py-16 text-muted-foreground">
          <Mail size={48} className="mx-auto mb-4 opacity-30" />
          <p className="text-lg font-medium">No campaigns yet</p>
          <p className="text-sm">Create your first campaign to get started</p>
        </div>
      ) : (
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full">
            <thead className="bg-accent">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Campaign</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Subject</th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Created</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {campaigns.map((campaign) => {
                const status = statusConfig[campaign.status]
                const StatusIcon = status.icon
                return (
                  <tr
                    key={campaign.id}
                    className="hover:bg-accent/50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/campaigns/${campaign.id}`)}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-foreground text-sm">{campaign.name}</p>
                      {campaign.tags.length > 0 && (
                        <div className="flex gap-1 mt-1">
                          {campaign.tags.slice(0, 3).map((tag) => (
                            <span key={tag} className="text-xs bg-secondary text-muted-foreground px-1.5 py-0.5 rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className={cn('flex items-center gap-1.5 text-sm', status.color)}>
                        <StatusIcon size={14} />
                        {status.label}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground max-w-xs truncate">
                      {campaign.subject_line || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      {campaign.status === 'draft' && (
                        <button
                          onClick={() => deleteMutation.mutate(campaign.id)}
                          className="text-xs text-muted-foreground hover:text-destructive transition-colors"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create `frontend/src/features/campaigns/CreateCampaignWizard.tsx`**

```typescript
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateCampaign } from './useCampaigns'
import { useTemplates } from '@/features/templates/useTemplates'
import { getOrgSlug } from '@/lib/utils'

export default function CreateCampaignWizard() {
  const navigate = useNavigate()
  const createMutation = useCreateCampaign()
  const { data: templates } = useTemplates()
  const [form, setForm] = useState({
    name: '',
    subject_line: '',
    preview_text: '',
    from_name: '',
    from_email: '',
    reply_to: '',
    tags: [] as string[],
    template_id: '',
  })
  const [tagInput, setTagInput] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = {
      ...form,
      template_id: form.template_id || undefined,
    }
    const campaign = await createMutation.mutateAsync(payload)
    if (form.template_id) {
      navigate(`/editor/${form.template_id}?campaign_id=${campaign.id}`)
    } else {
      navigate(`/campaigns/${campaign.id}`)
    }
  }

  const addTag = () => {
    if (tagInput.trim() && !form.tags.includes(tagInput.trim())) {
      setForm((f) => ({ ...f, tags: [...f.tags, tagInput.trim()] }))
      setTagInput('')
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">New Campaign</h1>
        <p className="text-muted-foreground text-sm mt-1">Set up your email campaign details</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-card rounded-xl border border-border p-6">
        {/* Campaign Name */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Campaign Name *</label>
          <input
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="e.g. Cloud Transformation Q1 2026"
          />
        </div>

        {/* Subject Line */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Subject Line</label>
          <input
            value={form.subject_line}
            onChange={(e) => setForm((f) => ({ ...f, subject_line: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Transform Your Enterprise Operations"
          />
          <p className="text-xs text-muted-foreground mt-1">{form.subject_line.length}/300 characters</p>
        </div>

        {/* Preview Text */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Preview Text</label>
          <input
            value={form.preview_text}
            onChange={(e) => setForm((f) => ({ ...f, preview_text: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Discover scalable solutions for your business..."
          />
        </div>

        {/* From */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">From Name</label>
            <input
              value={form.from_name}
              onChange={(e) => setForm((f) => ({ ...f, from_name: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Maven Technosoft"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">From Email</label>
            <input
              type="email"
              value={form.from_email}
              onChange={(e) => setForm((f) => ({ ...f, from_email: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="noreply@maven.com"
            />
          </div>
        </div>

        {/* Template */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Email Template (optional)</label>
          <select
            value={form.template_id}
            onChange={(e) => setForm((f) => ({ ...f, template_id: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Start from scratch</option>
            {templates?.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Tags</label>
          <div className="flex gap-2 mb-2">
            <input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              className="flex-1 px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
              placeholder="Add tag and press Enter"
            />
            <button
              type="button"
              onClick={addTag}
              className="px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-1">
            {form.tags.map((tag) => (
              <span
                key={tag}
                onClick={() => setForm((f) => ({ ...f, tags: f.tags.filter((t) => t !== tag) }))}
                className="text-xs bg-primary/10 text-primary px-2 py-1 rounded cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors"
              >
                {tag} ×
              </span>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-2">
          <button
            type="button"
            onClick={() => navigate('/campaigns')}
            className="px-4 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            {createMutation.isPending ? 'Creating...' : form.template_id ? 'Create & Open Editor' : 'Create Campaign'}
          </button>
        </div>
      </form>
    </div>
  )
}
```

- [ ] **Step 4: Create `frontend/src/features/campaigns/CampaignDetail.tsx`**

```typescript
import { useParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useCampaign, useUpdateCampaign, useSendCampaign, useScheduleCampaign } from './useCampaigns'
import { AIPanel } from '@/features/ai/AIPanel'
import { Send, Edit3, Clock } from 'lucide-react'

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: campaign, isLoading } = useCampaign(id!)
  const sendMutation = useSendCampaign()
  const [showSchedule, setShowSchedule] = useState(false)
  const [scheduledAt, setScheduledAt] = useState('')
  const scheduleMutation = useScheduleCampaign()
  const [showAI, setShowAI] = useState(false)

  if (isLoading || !campaign) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{campaign.name}</h1>
          <span className={`text-xs px-2 py-1 rounded font-medium mt-1 inline-block ${
            campaign.status === 'draft' ? 'bg-secondary text-muted-foreground' :
            campaign.status === 'sent' ? 'bg-green-500/10 text-green-400' :
            campaign.status === 'failed' ? 'bg-destructive/10 text-destructive' :
            'bg-yellow-500/10 text-yellow-400'
          }`}>
            {campaign.status.toUpperCase()}
          </span>
        </div>
        {campaign.status === 'draft' && (
          <div className="flex gap-2">
            <button
              onClick={() => setShowAI(!showAI)}
              className="px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              🤖 AI Assist
            </button>
            <button
              onClick={() => campaign.template && navigate(`/editor/${campaign.template}`)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              <Edit3 size={14} /> Edit Template
            </button>
            <button
              onClick={() => setShowSchedule(true)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              <Clock size={14} /> Schedule
            </button>
            <button
              onClick={() => sendMutation.mutate(id!)}
              disabled={sendMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              <Send size={14} />
              {sendMutation.isPending ? 'Queuing...' : 'Send Now'}
            </button>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {[
          { label: 'Subject Line', value: campaign.subject_line || '—' },
          { label: 'Preview Text', value: campaign.preview_text || '—' },
          { label: 'From', value: campaign.from_email ? `${campaign.from_name} <${campaign.from_email}>` : '—' },
          { label: 'Reply To', value: campaign.reply_to || '—' },
        ].map(({ label, value }) => (
          <div key={label} className="bg-card rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">{label}</p>
            <p className="text-sm text-foreground">{value}</p>
          </div>
        ))}
      </div>

      {/* AI Panel */}
      {showAI && <AIPanel campaignId={id!} />}

      {/* Schedule Modal */}
      {showSchedule && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl border border-border p-6 w-96">
            <h3 className="font-semibold text-foreground mb-4">Schedule Campaign</h3>
            <input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground mb-4 focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="flex gap-2 justify-end">
              <button onClick={() => setShowSchedule(false)} className="px-3 py-2 rounded-lg border border-border text-sm text-muted-foreground">Cancel</button>
              <button
                onClick={async () => {
                  await scheduleMutation.mutateAsync({ id: id!, scheduled_at: new Date(scheduledAt).toISOString() })
                  setShowSchedule(false)
                }}
                disabled={!scheduledAt || scheduleMutation.isPending}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm disabled:opacity-50"
              >
                Schedule
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/features/campaigns/
git commit -m "feat: campaigns list, create wizard, detail page"
```

---

## Task 5: Templates + GrapesJS Editor

**Files:**
- Create: `frontend/src/features/templates/useTemplates.ts`
- Create: `frontend/src/features/templates/TemplateLibrary.tsx`
- Create: `frontend/src/features/templates/TemplateCard.tsx`
- Create: `frontend/src/features/editor/useEditorStore.ts`
- Create: `frontend/src/features/editor/GrapesEditor.tsx`
- Create: `frontend/src/features/editor/EditorPage.tsx`
- Create: `frontend/src/features/editor/SubjectLineBar.tsx`

- [ ] **Step 1: Create `frontend/src/features/templates/useTemplates.ts`**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { EmailTemplate } from '@/types'

export function useTemplates(category?: string) {
  const orgSlug = getOrgSlug()
  return useQuery<EmailTemplate[]>({
    queryKey: ['templates', orgSlug, category],
    queryFn: async () => {
      const params = new URLSearchParams({ org_slug: orgSlug })
      if (category) params.append('category', category)
      const { data } = await api.get(`/templates/?${params}`)
      return data
    },
    enabled: !!orgSlug,
  })
}

export function useTemplate(id: string) {
  const orgSlug = getOrgSlug()
  return useQuery<EmailTemplate>({
    queryKey: ['template', id],
    queryFn: async () => {
      const { data } = await api.get(`/templates/${id}?org_slug=${orgSlug}`)
      return data
    },
    enabled: !!id && !!orgSlug,
  })
}

export function useSaveTemplate(id: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: Partial<EmailTemplate>) =>
      api.patch(`/templates/${id}?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['template', id] })
      qc.invalidateQueries({ queryKey: ['templates'] })
    },
  })
}

export function useCreateTemplate() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: { name: string; category: string }) =>
      api.post(`/templates/?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] }),
  })
}

export function useDuplicateTemplate() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (id: string) =>
      api.post(`/templates/${id}/duplicate?org_slug=${orgSlug}`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] }),
  })
}
```

- [ ] **Step 2: Create `frontend/src/features/templates/TemplateCard.tsx`**

```typescript
import { useNavigate } from 'react-router-dom'
import { Copy, Edit3, Lock } from 'lucide-react'
import type { EmailTemplate } from '@/types'
import { useDuplicateTemplate } from './useTemplates'

interface Props {
  template: EmailTemplate
}

export default function TemplateCard({ template }: Props) {
  const navigate = useNavigate()
  const duplicateMutation = useDuplicateTemplate()

  return (
    <div className="group bg-card border border-border rounded-xl overflow-hidden hover:border-primary/50 transition-colors">
      {/* Thumbnail */}
      <div className="h-40 bg-accent flex items-center justify-center relative">
        {template.thumbnail_url ? (
          <img src={template.thumbnail_url} alt={template.name} className="w-full h-full object-cover" />
        ) : (
          <div className="text-center text-muted-foreground">
            <div className="text-4xl mb-2">📧</div>
            <p className="text-xs">{template.category}</p>
          </div>
        )}
        {template.is_system && (
          <div className="absolute top-2 right-2">
            <span className="flex items-center gap-1 text-xs bg-primary/20 text-primary px-2 py-1 rounded">
              <Lock size={10} /> System
            </span>
          </div>
        )}
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={() => navigate(`/editor/${template.id}`)}
            className="flex items-center gap-1.5 px-3 py-2 bg-primary text-white rounded-lg text-xs font-medium"
          >
            <Edit3 size={12} /> Edit
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); duplicateMutation.mutate(template.id) }}
            className="flex items-center gap-1.5 px-3 py-2 bg-white/20 text-white rounded-lg text-xs"
          >
            <Copy size={12} /> Copy
          </button>
        </div>
      </div>
      {/* Info */}
      <div className="p-3">
        <p className="font-medium text-foreground text-sm truncate">{template.name}</p>
        <p className="text-xs text-muted-foreground mt-0.5 capitalize">{template.category}</p>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create `frontend/src/features/templates/TemplateLibrary.tsx`**

```typescript
import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useTemplates, useCreateTemplate } from './useTemplates'
import TemplateCard from './TemplateCard'
import { useNavigate } from 'react-router-dom'

const CATEGORIES = ['All', 'promo', 'newsletter', 'announcement', 'webinar', 'onboarding', 'outreach']

export default function TemplateLibrary() {
  const [category, setCategory] = useState<string | undefined>()
  const { data: templates, isLoading } = useTemplates(category)
  const createMutation = useCreateTemplate()
  const navigate = useNavigate()

  const handleCreate = async () => {
    const template = await createMutation.mutateAsync({ name: 'New Template', category: 'promo' })
    navigate(`/editor/${template.id}`)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Email Templates</h1>
          <p className="text-muted-foreground text-sm mt-1">{templates?.length || 0} templates</p>
        </div>
        <button
          onClick={handleCreate}
          disabled={createMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          <Plus size={16} /> New Template
        </button>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat === 'All' ? undefined : cat)}
            className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-colors ${
              (cat === 'All' && !category) || cat === category
                ? 'bg-primary text-primary-foreground'
                : 'bg-accent text-muted-foreground hover:text-foreground'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {templates?.map((t) => (
            <TemplateCard key={t.id} template={t} />
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Create `frontend/src/features/editor/useEditorStore.ts`**

```typescript
import { create } from 'zustand'

interface EditorState {
  gjsData: { components: unknown; styles: unknown } | null
  isDirty: boolean
  previewMode: 'desktop' | 'mobile'
  lastSaved: Date | null
  setGjsData: (data: { components: unknown; styles: unknown }) => void
  setPreviewMode: (mode: 'desktop' | 'mobile') => void
  markSaved: () => void
  markDirty: () => void
}

export const useEditorStore = create<EditorState>((set) => ({
  gjsData: null,
  isDirty: false,
  previewMode: 'desktop',
  lastSaved: null,
  setGjsData: (data) => set({ gjsData: data }),
  setPreviewMode: (mode) => set({ previewMode: mode }),
  markSaved: () => set({ isDirty: false, lastSaved: new Date() }),
  markDirty: () => set({ isDirty: true }),
}))
```

- [ ] **Step 5: Create `frontend/src/features/editor/GrapesEditor.tsx`**

```typescript
import { useEffect, useRef } from 'react'
import grapesjs from 'grapesjs'
import 'grapesjs/dist/css/grapes.min.css'
// @ts-ignore — grapesjs-mjml has no types
import gjsMjml from 'grapesjs-mjml'
import 'grapesjs-mjml/dist/grapesjs-mjml.min.css'
import type { EmailTemplate } from '@/types'
import { useEditorStore } from './useEditorStore'

interface Props {
  template: EmailTemplate
  onSave: (data: { gjs_components: unknown; gjs_styles: unknown; mjml_source: string; html_output: string }) => void
}

export default function GrapesEditor({ template, onSave }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const editorRef = useRef<any>(null)
  const { setGjsData, markDirty, markSaved } = useEditorStore()

  useEffect(() => {
    if (!containerRef.current || editorRef.current) return

    const editor = grapesjs.init({
      container: containerRef.current,
      plugins: [gjsMjml],
      pluginsOpts: {
        [gjsMjml as any]: {},
      },
      storageManager: false,
      // Load initial data from template
      components: template.gjs_components ? JSON.stringify(template.gjs_components) : undefined,
      style: template.gjs_styles ? JSON.stringify(template.gjs_styles) : undefined,
    })

    editorRef.current = editor

    // Mark dirty on any change
    editor.on('change:changesCount', () => markDirty())

    // Auto-save every 30 seconds
    const autoSaveInterval = setInterval(() => {
      handleSave(editor)
    }, 30_000)

    return () => {
      clearInterval(autoSaveInterval)
      editor.destroy()
      editorRef.current = null
    }
  }, [template.id])

  const handleSave = (editor: any) => {
    const components = editor.getComponents().toJSON()
    const styles = editor.getStyle().toJSON()

    // Get MJML source from editor
    const mjmlSource = editor.runCommand('mjml-code-viewer') || ''

    // Get compiled HTML
    const htmlOutput = editor.runCommand('preview') || editor.getHtml()

    const data = {
      gjs_components: components,
      gjs_styles: styles,
      mjml_source: typeof mjmlSource === 'string' ? mjmlSource : '',
      html_output: typeof htmlOutput === 'string' ? htmlOutput : '',
    }

    setGjsData({ components, styles })
    onSave(data)
    markSaved()
  }

  return (
    <div
      ref={containerRef}
      style={{ height: '100%', width: '100%' }}
      className="gjs-editor-wrap"
    />
  )
}
```

- [ ] **Step 6: Create `frontend/src/features/editor/SubjectLineBar.tsx`**

```typescript
import { useState } from 'react'
import { getOrgSlug } from '@/lib/utils'
import api from '@/lib/api'
import { useAIStore } from '@/features/ai/useAIStore'

interface Props {
  campaignId?: string
  subjectLine: string
  onSubjectChange: (value: string) => void
}

export default function SubjectLineBar({ campaignId, subjectLine, onSubjectChange }: Props) {
  const charCount = subjectLine.length
  const isLong = charCount > 60
  const isOverLimit = charCount > 300

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-card border-b border-border">
      <span className="text-xs text-muted-foreground whitespace-nowrap">Subject:</span>
      <input
        value={subjectLine}
        onChange={(e) => onSubjectChange(e.target.value)}
        className="flex-1 bg-transparent text-foreground text-sm focus:outline-none placeholder:text-muted-foreground"
        placeholder="Enter subject line..."
        maxLength={300}
      />
      <span className={`text-xs whitespace-nowrap ${isOverLimit ? 'text-destructive' : isLong ? 'text-yellow-400' : 'text-muted-foreground'}`}>
        {charCount}/300
      </span>
      {isLong && <span className="text-xs text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded">Long</span>}
    </div>
  )
}
```

- [ ] **Step 7: Create `frontend/src/features/editor/EditorPage.tsx`**

```typescript
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useState, useCallback } from 'react'
import { Monitor, Smartphone, Save, ArrowLeft } from 'lucide-react'
import { useTemplate, useSaveTemplate } from '@/features/templates/useTemplates'
import { useEditorStore } from './useEditorStore'
import GrapesEditor from './GrapesEditor'
import SubjectLineBar from './SubjectLineBar'
import { AIPanel } from '@/features/ai/AIPanel'
import TopBar from '@/components/shared/TopBar'
import { useUpdateCampaign } from '@/features/campaigns/useCampaigns'
import { useDebouncedCallback } from 'use-debounce'

export default function EditorPage() {
  const { templateId } = useParams<{ templateId: string }>()
  const [searchParams] = useSearchParams()
  const campaignId = searchParams.get('campaign_id') || undefined
  const navigate = useNavigate()
  const { data: template, isLoading } = useTemplate(templateId!)
  const saveMutation = useSaveTemplate(templateId!)
  const updateCampaign = useUpdateCampaign(campaignId || '')
  const { previewMode, setPreviewMode, isDirty, lastSaved } = useEditorStore()
  const [subjectLine, setSubjectLine] = useState('')
  const [showAI, setShowAI] = useState(false)

  const handleSave = useCallback(
    async (data: {
      gjs_components: unknown
      gjs_styles: unknown
      mjml_source: string
      html_output: string
    }) => {
      await saveMutation.mutateAsync(data)
      if (campaignId && subjectLine) {
        await updateCampaign.mutateAsync({ subject_line: subjectLine })
      }
    },
    [campaignId, subjectLine]
  )

  if (isLoading || !template) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Editor TopBar */}
      <div className="flex items-center justify-between px-4 py-2 bg-card border-b border-border h-12 flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors text-sm"
          >
            <ArrowLeft size={16} />
            Back
          </button>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium text-foreground">{template.name}</span>
          {isDirty && <span className="text-xs text-yellow-400">● Unsaved</span>}
          {!isDirty && lastSaved && (
            <span className="text-xs text-muted-foreground">Saved {lastSaved.toLocaleTimeString()}</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Preview toggle */}
          <div className="flex items-center bg-accent rounded-lg p-0.5">
            <button
              onClick={() => setPreviewMode('desktop')}
              className={`p-1.5 rounded-md transition-colors ${previewMode === 'desktop' ? 'bg-card text-foreground' : 'text-muted-foreground'}`}
            >
              <Monitor size={15} />
            </button>
            <button
              onClick={() => setPreviewMode('mobile')}
              className={`p-1.5 rounded-md transition-colors ${previewMode === 'mobile' ? 'bg-card text-foreground' : 'text-muted-foreground'}`}
            >
              <Smartphone size={15} />
            </button>
          </div>
          <button
            onClick={() => setShowAI(!showAI)}
            className="px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:bg-accent text-xs"
          >
            🤖 AI
          </button>
          <button
            onClick={() => {
              // Trigger save via editor
              const event = new CustomEvent('editor:save-request')
              window.dispatchEvent(event)
            }}
            disabled={saveMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            <Save size={13} />
            {saveMutation.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Subject line bar (only when campaign context) */}
      {campaignId && (
        <SubjectLineBar
          campaignId={campaignId}
          subjectLine={subjectLine}
          onSubjectChange={setSubjectLine}
        />
      )}

      {/* Main editor area */}
      <div className="flex flex-1 overflow-hidden">
        <div className={`flex-1 transition-all ${showAI ? 'mr-80' : ''}`}>
          <GrapesEditor template={template} onSave={handleSave} />
        </div>

        {/* AI Sidebar */}
        {showAI && (
          <div className="w-80 border-l border-border bg-card overflow-y-auto flex-shrink-0 absolute right-0 top-12 bottom-0">
            <AIPanel campaignId={campaignId} />
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 8: Commit**

```bash
git add frontend/src/features/templates/ frontend/src/features/editor/
git commit -m "feat: template library, GrapesJS editor, subject line bar"
```

---

## Task 6: AI Panel + SSE Stream

**Files:**
- Create: `frontend/src/features/ai/useAIStore.ts`
- Create: `frontend/src/features/ai/useSSEStream.ts`
- Create: `frontend/src/features/ai/AIPanel.tsx`
- Create: `frontend/src/features/ai/SubjectSuggestions.tsx`
- Create: `frontend/src/features/ai/SpamChecker.tsx`

- [ ] **Step 1: Create `frontend/src/features/ai/useAIStore.ts`**

```typescript
import { create } from 'zustand'

interface AIState {
  isStreaming: boolean
  streamBuffer: string
  jobType: string | null
  suggestions: string[]
  currentJobId: string | null
  setStreaming: (v: boolean) => void
  appendToBuffer: (chunk: string) => void
  clearBuffer: () => void
  setJobType: (type: string) => void
  setJobId: (id: string) => void
  addSuggestion: (s: string) => void
  clearSuggestions: () => void
}

export const useAIStore = create<AIState>((set) => ({
  isStreaming: false,
  streamBuffer: '',
  jobType: null,
  suggestions: [],
  currentJobId: null,
  setStreaming: (v) => set({ isStreaming: v }),
  appendToBuffer: (chunk) => set((s) => ({ streamBuffer: s.streamBuffer + chunk })),
  clearBuffer: () => set({ streamBuffer: '' }),
  setJobType: (type) => set({ jobType: type }),
  setJobId: (id) => set({ currentJobId: id }),
  addSuggestion: (s) => set((state) => ({ suggestions: [...state.suggestions, s] })),
  clearSuggestions: () => set({ suggestions: [] }),
}))
```

- [ ] **Step 2: Create `frontend/src/features/ai/useSSEStream.ts`**

```typescript
import { useCallback } from 'react'
import { useAIStore } from './useAIStore'
import { getOrgSlug } from '@/lib/utils'

interface StreamOptions {
  jobType: string
  inputData: Record<string, unknown>
  campaignId?: string
  onComplete?: (fullText: string) => void
}

export function useSSEStream() {
  const { setStreaming, appendToBuffer, clearBuffer, setJobType, setJobId } = useAIStore()

  const startStream = useCallback(async (options: StreamOptions) => {
    const orgSlug = getOrgSlug()
    const token = localStorage.getItem('access_token')
    if (!orgSlug || !token) return

    setJobType(options.jobType)
    clearBuffer()
    setStreaming(true)

    try {
      // First, POST to create the job and get the streaming response
      const response = await fetch(`/api/ai/stream?org_slug=${orgSlug}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          job_type: options.jobType,
          input_data: options.inputData,
          campaign_id: options.campaignId || null,
        }),
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        // Parse SSE events
        const lines = text.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              if (event.type === 'job_id') {
                setJobId(event.job_id)
              } else if (event.type === 'chunk') {
                appendToBuffer(event.content)
                fullText += event.content
              } else if (event.type === 'done') {
                options.onComplete?.(fullText)
              }
            } catch {}
          }
        }
      }
    } catch (error) {
      console.error('SSE stream error:', error)
    } finally {
      setStreaming(false)
    }
  }, [])

  return { startStream }
}
```

- [ ] **Step 3: Create `frontend/src/features/ai/SubjectSuggestions.tsx`**

```typescript
import { useState } from 'react'
import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { Sparkles, Copy, Check } from 'lucide-react'

interface Props {
  campaignId?: string
  onSelect?: (subject: string) => void
}

export default function SubjectSuggestions({ campaignId, onSelect }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType } = useAIStore()
  const [industry, setIndustry] = useState('Technology')
  const [tone, setTone] = useState('professional')
  const [copied, setCopied] = useState<number | null>(null)

  const isActive = isStreaming && jobType === 'subject_lines'

  const handleGenerate = () => {
    startStream({
      jobType: 'subject_lines',
      inputData: { campaign_name: 'Campaign', industry, tone },
      campaignId,
    })
  }

  // Parse numbered lines from stream buffer
  const lines = streamBuffer
    .split('\n')
    .filter((l) => /^\d+\./.test(l.trim()))
    .map((l) => l.replace(/^\d+\.\s*/, '').trim())

  const handleCopy = (line: string, idx: number) => {
    navigator.clipboard.writeText(line)
    setCopied(idx)
    setTimeout(() => setCopied(null), 1500)
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
        >
          <option>Technology</option>
          <option>Travel & Logistics</option>
          <option>Cloud Computing</option>
          <option>Analytics</option>
          <option>Enterprise</option>
        </select>
        <select
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
        >
          <option value="professional">Professional</option>
          <option value="urgent">Urgent</option>
          <option value="friendly">Friendly</option>
          <option value="authoritative">Authoritative</option>
        </select>
      </div>

      <button
        onClick={handleGenerate}
        disabled={isActive}
        className="w-full flex items-center justify-center gap-2 py-2 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 disabled:opacity-50"
      >
        <Sparkles size={13} />
        {isActive ? 'Generating...' : 'Generate 5 Subject Lines'}
      </button>

      {isActive && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
          AI is writing...
        </div>
      )}

      {lines.length > 0 && (
        <div className="space-y-2">
          {lines.map((line, idx) => (
            <div
              key={idx}
              className="flex items-start justify-between gap-2 p-2 bg-accent rounded-lg group"
            >
              <p className="text-xs text-foreground flex-1">{line}</p>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleCopy(line, idx)}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {copied === idx ? <Check size={12} className="text-green-400" /> : <Copy size={12} />}
                </button>
                {onSelect && (
                  <button
                    onClick={() => onSelect(line)}
                    className="text-xs text-primary hover:underline"
                  >
                    Use
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {!isActive && streamBuffer && lines.length === 0 && (
        <p className="text-xs text-muted-foreground whitespace-pre-wrap">{streamBuffer}</p>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Create `frontend/src/features/ai/SpamChecker.tsx`**

```typescript
import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { ShieldCheck } from 'lucide-react'

interface Props {
  subject: string
  body: string
}

export default function SpamChecker({ subject, body }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType } = useAIStore()
  const isActive = isStreaming && jobType === 'spam_check'

  const handleCheck = () => {
    startStream({
      jobType: 'spam_check',
      inputData: { subject, body: body.slice(0, 2000) },
    })
  }

  // Extract spam score if present
  const scoreMatch = streamBuffer.match(/SPAM SCORE:\s*(\d+)/i)
  const score = scoreMatch ? parseInt(scoreMatch[1]) : null

  return (
    <div className="space-y-3">
      <button
        onClick={handleCheck}
        disabled={isActive}
        className="w-full flex items-center justify-center gap-2 py-2 bg-accent text-foreground rounded-lg text-xs font-medium hover:bg-accent/80 border border-border disabled:opacity-50"
      >
        <ShieldCheck size={13} />
        {isActive ? 'Analyzing...' : 'Check Spam Score'}
      </button>

      {score !== null && (
        <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
          <div
            className="text-2xl font-bold"
            style={{ color: score < 30 ? '#4ade80' : score < 60 ? '#facc15' : '#ef4444' }}
          >
            {score}
          </div>
          <div>
            <p className="text-xs font-medium text-foreground">Spam Score</p>
            <p className="text-xs text-muted-foreground">
              {score < 30 ? 'Low risk' : score < 60 ? 'Medium risk' : 'High risk — action needed'}
            </p>
          </div>
        </div>
      )}

      {streamBuffer && (
        <div className="text-xs text-muted-foreground whitespace-pre-wrap bg-accent/50 p-3 rounded-lg font-mono leading-relaxed">
          {streamBuffer}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 5: Create `frontend/src/features/ai/AIPanel.tsx`**

```typescript
import { useState } from 'react'
import SubjectSuggestions from './SubjectSuggestions'
import SpamChecker from './SpamChecker'
import { Sparkles, ShieldCheck, Pen, Target } from 'lucide-react'

interface Props {
  campaignId?: string
  subjectLine?: string
  emailBody?: string
}

type Tab = 'subject' | 'spam' | 'copy' | 'cta'

const tabs: { id: Tab; label: string; icon: any }[] = [
  { id: 'subject', label: 'Subject', icon: Sparkles },
  { id: 'spam', label: 'Spam', icon: ShieldCheck },
  { id: 'copy', label: 'Copy', icon: Pen },
  { id: 'cta', label: 'CTA', icon: Target },
]

export function AIPanel({ campaignId, subjectLine = '', emailBody = '' }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('subject')

  return (
    <div className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm font-semibold text-foreground">🤖 AI Assistant</span>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-4 gap-1 mb-4 bg-accent rounded-lg p-1">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex flex-col items-center py-1.5 rounded-md text-xs transition-colors ${
              activeTab === id ? 'bg-card text-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Icon size={12} className="mb-0.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'subject' && (
        <SubjectSuggestions campaignId={campaignId} />
      )}
      {activeTab === 'spam' && (
        <SpamChecker subject={subjectLine} body={emailBody} />
      )}
      {activeTab === 'copy' && (
        <CopyOptimizerTab emailBody={emailBody} />
      )}
      {activeTab === 'cta' && (
        <CTATab campaignId={campaignId} />
      )}
    </div>
  )
}

function CopyOptimizerTab({ emailBody }: { emailBody: string }) {
  const { startStream } = require('./useSSEStream').useSSEStream()
  const { isStreaming, streamBuffer, jobType } = require('./useAIStore').useAIStore()
  const isActive = isStreaming && jobType === 'copy_optimize'

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground">Paste or edit email body in the editor, then optimize with AI.</p>
      <button
        onClick={() => startStream({ jobType: 'copy_optimize', inputData: { copy: emailBody, tone: 'professional' } })}
        disabled={isActive || !emailBody}
        className="w-full py-2 bg-accent text-foreground rounded-lg text-xs font-medium border border-border disabled:opacity-50"
      >
        {isActive ? 'Optimizing...' : 'Optimize Copy'}
      </button>
      {streamBuffer && jobType === 'copy_optimize' && (
        <div className="text-xs text-foreground whitespace-pre-wrap bg-accent/50 p-3 rounded-lg leading-relaxed">
          {streamBuffer}
        </div>
      )}
    </div>
  )
}

function CTATab({ campaignId }: { campaignId?: string }) {
  const { startStream } = require('./useSSEStream').useSSEStream()
  const { isStreaming, streamBuffer, jobType } = require('./useAIStore').useAIStore()
  const [goal, setGoal] = useState<string>('schedule a demo')
  const isActive = isStreaming && jobType === 'cta_suggest'

  return (
    <div className="space-y-3">
      <select
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        className="w-full px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
      >
        <option value="schedule a demo">Schedule a Demo</option>
        <option value="learn more">Learn More</option>
        <option value="contact us">Contact Us</option>
        <option value="start free trial">Start Free Trial</option>
        <option value="book consultation">Book Consultation</option>
      </select>
      <button
        onClick={() => startStream({ jobType: 'cta_suggest', inputData: { campaign_goal: goal, industry: 'Technology' } })}
        disabled={isActive}
        className="w-full py-2 bg-accent text-foreground rounded-lg text-xs font-medium border border-border disabled:opacity-50"
      >
        {isActive ? 'Generating...' : 'Generate CTAs'}
      </button>
      {streamBuffer && jobType === 'cta_suggest' && (
        <div className="text-xs text-foreground whitespace-pre-wrap bg-accent/50 p-3 rounded-lg leading-relaxed">
          {streamBuffer}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/ai/
git commit -m "feat: AI panel with SSE streaming, subject suggestions, spam checker, copy optimizer, CTA"
```

---

## Task 7: Settings Pages

**Files:**
- Create: `frontend/src/features/settings/SettingsLayout.tsx`
- Create: `frontend/src/features/settings/SMTPSetup.tsx`
- Create: `frontend/src/features/settings/OrgSettings.tsx`
- Create: `frontend/src/features/settings/UserManagement.tsx`

- [ ] **Step 1: Create `frontend/src/features/settings/SettingsLayout.tsx`**

```typescript
import { NavLink, Outlet } from 'react-router-dom'
import { Building2, Mail, Users } from 'lucide-react'
import { cn } from '@/lib/utils'

const settingsNav = [
  { to: '/settings', label: 'Organization', icon: Building2, end: true },
  { to: '/settings/smtp', label: 'SMTP Setup', icon: Mail },
  { to: '/settings/users', label: 'Users', icon: Users },
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
                  isActive ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-accent hover:text-foreground'
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
```

- [ ] **Step 2: Create `frontend/src/features/settings/SMTPSetup.tsx`**

```typescript
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { SMTPConfig } from '@/types'
import { CheckCircle, XCircle } from 'lucide-react'

export default function SMTPSetup() {
  const orgSlug = getOrgSlug()
  const qc = useQueryClient()
  const { data: smtp } = useQuery<SMTPConfig>({
    queryKey: ['smtp', orgSlug],
    queryFn: async () => {
      const { data } = await api.get(`/settings/smtp?org_slug=${orgSlug}`)
      return data
    },
  })

  const [form, setForm] = useState({
    host: smtp?.host || '',
    port: smtp?.port || 587,
    username: smtp?.username || '',
    password: '',
    use_tls: smtp?.use_tls ?? true,
    use_ssl: smtp?.use_ssl ?? false,
  })
  const [testEmail, setTestEmail] = useState('')
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)

  const saveMutation = useMutation({
    mutationFn: (payload: typeof form) =>
      api.put(`/settings/smtp?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['smtp'] }),
  })

  const testMutation = useMutation({
    mutationFn: (to_email: string) =>
      api.post(`/settings/smtp/test?org_slug=${orgSlug}`, { to_email }).then((r) => r.data),
    onSuccess: (data) => setTestResult(data),
  })

  return (
    <div className="max-w-lg">
      <h2 className="text-xl font-bold text-foreground mb-1">SMTP Configuration</h2>
      <p className="text-muted-foreground text-sm mb-6">Configure your outgoing mail server</p>

      <form
        onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(form) }}
        className="space-y-4 bg-card rounded-xl border border-border p-5"
      >
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="block text-xs font-medium text-muted-foreground mb-1">SMTP Host</label>
            <input
              value={form.host}
              onChange={(e) => setForm((f) => ({ ...f, host: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="smtp.gmail.com"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">Port</label>
            <input
              type="number"
              value={form.port}
              onChange={(e) => setForm((f) => ({ ...f, port: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">Username</label>
          <input
            value={form.username}
            onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">Password</label>
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Leave blank to keep current"
          />
        </div>

        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.use_tls}
              onChange={(e) => setForm((f) => ({ ...f, use_tls: e.target.checked }))}
              className="w-4 h-4 accent-primary"
            />
            <span className="text-sm text-foreground">Use TLS</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.use_ssl}
              onChange={(e) => setForm((f) => ({ ...f, use_ssl: e.target.checked }))}
              className="w-4 h-4 accent-primary"
            />
            <span className="text-sm text-foreground">Use SSL</span>
          </label>
        </div>

        <div className="flex gap-2 pt-2">
          <button
            type="submit"
            disabled={saveMutation.isPending}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            {saveMutation.isPending ? 'Saving...' : 'Save Config'}
          </button>
        </div>
      </form>

      {/* Test connection */}
      {smtp && (
        <div className="mt-4 bg-card rounded-xl border border-border p-5">
          <h3 className="text-sm font-semibold text-foreground mb-3">Test Connection</h3>
          <div className="flex gap-2">
            <input
              type="email"
              value={testEmail}
              onChange={(e) => setTestEmail(e.target.value)}
              placeholder="Send test email to..."
              className="flex-1 px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              onClick={() => testMutation.mutate(testEmail)}
              disabled={!testEmail || testMutation.isPending}
              className="px-4 py-2 bg-accent text-foreground rounded-lg text-sm border border-border disabled:opacity-50"
            >
              Test
            </button>
          </div>
          {testResult && (
            <div className={`flex items-center gap-2 mt-3 text-sm ${testResult.success ? 'text-green-400' : 'text-destructive'}`}>
              {testResult.success ? <CheckCircle size={16} /> : <XCircle size={16} />}
              {testResult.message}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create `frontend/src/features/settings/OrgSettings.tsx`**

```typescript
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'

export default function OrgSettings() {
  const orgSlug = getOrgSlug()
  const qc = useQueryClient()

  const { data: org } = useQuery({
    queryKey: ['org', orgSlug],
    queryFn: async () => {
      const { data } = await api.get(`/orgs/${orgSlug}`)
      return data
    },
  })

  const [orgName, setOrgName] = useState(org?.name || '')
  const [aiKey, setAiKey] = useState('')

  const updateMutation = useMutation({
    mutationFn: (payload: { name?: string }) =>
      api.patch(`/orgs/${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['org'] }),
  })

  const aiKeyMutation = useMutation({
    mutationFn: (key: string) =>
      api.put(`/settings/ai-key?org_slug=${orgSlug}`, { openai_api_key: key }).then((r) => r.data),
  })

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-xl font-bold text-foreground mb-1">Organization</h2>
        <p className="text-muted-foreground text-sm">Manage your organization settings</p>
      </div>

      <div className="bg-card rounded-xl border border-border p-5 space-y-4">
        <h3 className="text-sm font-semibold text-foreground">General</h3>
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">Organization Name</label>
          <input
            value={orgName || org?.name || ''}
            onChange={(e) => setOrgName(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          onClick={() => updateMutation.mutate({ name: orgName })}
          disabled={updateMutation.isPending}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save'}
        </button>
      </div>

      <div className="bg-card rounded-xl border border-border p-5 space-y-4">
        <h3 className="text-sm font-semibold text-foreground">OpenAI API Key</h3>
        <p className="text-xs text-muted-foreground">Required for AI features (subject lines, copy optimization, spam check)</p>
        <div>
          <input
            type="password"
            value={aiKey}
            onChange={(e) => setAiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          onClick={() => aiKeyMutation.mutate(aiKey)}
          disabled={!aiKey || aiKeyMutation.isPending}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          {aiKeyMutation.isPending ? 'Saving...' : 'Update API Key'}
        </button>
        {aiKeyMutation.isSuccess && (
          <p className="text-xs text-green-400">✓ API key updated</p>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/settings/
git commit -m "feat: settings pages — org settings, SMTP setup"
```

---

## Task 8: Final Build Check

- [ ] **Step 1: Add missing `use-debounce` package (used in EditorPage)**

```bash
cd frontend
npm install use-debounce
```

- [ ] **Step 2: Run TypeScript check**

```bash
npx tsc --noEmit
```

Fix any type errors before proceeding.

- [ ] **Step 3: Start both servers and verify end-to-end**

Terminal 1 (backend):
```bash
cd backend
python manage.py runserver
```

Terminal 2 (frontend):
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`

Expected flow:
1. `/login` page loads with Google OAuth button and email/password form
2. Login with test credentials → redirects to `/campaigns`
3. `/campaigns` shows empty state with "New Campaign" button
4. `/templates` shows template library grid
5. `/settings/smtp` shows SMTP setup form

- [ ] **Step 4: Build for production**

```bash
cd frontend
npm run build
```

Expected: `dist/` folder created with no build errors.

- [ ] **Step 5: Final commit**

```bash
cd "E:/career247/New folder (2)/project 1"
git add frontend/
git commit -m "feat: complete frontend Phase 1 — auth, campaigns, editor, AI panel, settings"
```

---

## Summary

| Task | Feature | Key Components |
|------|---------|----------------|
| 1 | Project scaffold | Vite, Tailwind, Zustand, TanStack, API client |
| 2 | Auth | LoginPage, useAuthStore, ProtectedRoute |
| 3 | App shell | AppShell, Sidebar, TopBar, router |
| 4 | Campaigns | CampaignList, CreateWizard, CampaignDetail |
| 5 | Templates + Editor | TemplateLibrary, GrapesEditor, SubjectLineBar, EditorPage |
| 6 | AI Panel | useSSEStream, useAIStore, SubjectSuggestions, SpamChecker |
| 7 | Settings | SMTPSetup, OrgSettings |
| 8 | Build check | TypeScript, dev servers, production build |

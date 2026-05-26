import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom'
import ProtectedRoute from '@/features/auth/ProtectedRoute'
import LoginPage from '@/features/auth/LoginPage'
import GoogleOAuthCallback from '@/features/auth/GoogleOAuthCallback'
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
  { path: '/auth/google/callback', element: <GoogleOAuthCallback /> },
  {
    path: '/',
    element: <ProtectedRoute><Navigate to="/campaigns" replace /></ProtectedRoute>,
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

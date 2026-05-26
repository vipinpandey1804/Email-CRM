import { Navigate } from 'react-router-dom'
import type { ReactNode } from 'react'
import { useAuthStore } from './useAuthStore'

interface Props {
  children: ReactNode
}

export default function ProtectedRoute({ children }: Props) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

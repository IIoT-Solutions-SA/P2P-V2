import React from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Login from '@/pages/Login'
import Signup from '@/pages/Signup'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()
  const [showSignup, setShowSignup] = React.useState(false)

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  // If not authenticated, show login/signup
  if (!isAuthenticated) {
    if (showSignup) {
      return (
        <Signup
          onNavigateToLogin={() => setShowSignup(false)}
          onSignupSuccess={() => {
            // Authentication state will be updated by the signup function
            // Component will re-render and show protected content
          }}
        />
      )
    }

    return (
      <Login
        onNavigateToSignup={() => setShowSignup(true)}
        onLoginSuccess={() => {
          // Authentication state will be updated by the login function
          // Component will re-render and show protected content
        }}
      />
    )
  }

  // If authenticated, render the protected content
  return <>{children}</>
}
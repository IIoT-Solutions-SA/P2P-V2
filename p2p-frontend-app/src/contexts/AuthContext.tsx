import React, { createContext, useContext, useState, useEffect } from 'react'
import Session from "supertokens-auth-react/recipe/session"
import { redirectToAuth } from "supertokens-auth-react"
import type { User, Organization, AuthState, LoginCredentials, SignupData } from '@/types/auth'

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Mock data for demonstration
const mockOrganizations: Organization[] = [
  {
    id: 'org-1',
    name: 'Advanced Electronics Co.',
    domain: 'advanced-electronics.com',
    industry: 'Electronics Manufacturing',
    size: 'medium',
    country: 'Saudi Arabia',
    city: 'Riyadh',
    isActive: true,
    createdAt: new Date('2023-01-15'),
    adminUserId: 'user-1'
  },
  {
    id: 'org-2',
    name: 'Gulf Plastics Industries',
    domain: 'gulf-plastics.com',
    industry: 'Plastics Manufacturing',
    size: 'large',
    country: 'Saudi Arabia',
    city: 'Dammam',
    isActive: true,
    createdAt: new Date('2023-03-20'),
    adminUserId: 'user-3'
  }
]

const mockUsers: User[] = [
  {
    id: 'user-1',
    email: 'ahmed.faisal@advanced-electronics.com',
    firstName: 'Ahmed',
    lastName: 'Al-Faisal',
    role: 'admin',
    organizationId: 'org-1',
    isActive: true,
    lastLogin: new Date(),
    createdAt: new Date('2023-01-15')
  },
  {
    id: 'user-2',
    email: 'sara.hassan@advanced-electronics.com',
    firstName: 'Sara',
    lastName: 'Hassan',
    role: 'member',
    organizationId: 'org-1',
    isActive: true,
    lastLogin: new Date('2024-01-20'),
    createdAt: new Date('2023-02-10')
  },
  {
    id: 'user-3',
    email: 'mohammed.rashid@gulf-plastics.com',
    firstName: 'Mohammed',
    lastName: 'Rashid',
    role: 'admin',
    organizationId: 'org-2',
    isActive: true,
    lastLogin: new Date('2024-01-22'),
    createdAt: new Date('2023-03-20')
  }
]

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    organization: null,
    isAuthenticated: false,
    isLoading: true
  })

  useEffect(() => {
    // Check SuperTokens session on app load
    const checkAuthState = async () => {
      try {
        const sessionExists = await Session.doesSessionExist()
        
        if (sessionExists) {
          // Fetch user profile from our backend API
          const response = await fetch('http://localhost:8000/api/v1/auth/me', {
            credentials: 'include' // Include SuperTokens cookies
          })
          
          if (response.ok) {
            const { user, organization } = await response.json()
            setAuthState({
              user,
              organization,
              isAuthenticated: true,
              isLoading: false
            })
          } else {
            setAuthState({
              user: null,
              organization: null,
              isAuthenticated: false,
              isLoading: false
            })
          }
        } else {
          setAuthState({
            user: null,
            organization: null,
            isAuthenticated: false,
            isLoading: false
          })
        }
      } catch (error) {
        console.error('Error checking auth state:', error)
        setAuthState({
          user: null,
          organization: null,
          isAuthenticated: false,
          isLoading: false
        })
      }
    }

    checkAuthState()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      // Call standard SuperTokens signin endpoint
      const response = await fetch('http://localhost:8000/api/v1/auth/signin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session
        body: JSON.stringify({
          formFields: [
            { id: "email", value: credentials.email },
            { id: "password", value: credentials.password }
          ]
        })
      })

      const result = await response.json()
      console.log('🔐 SuperTokens signin response:', result)

      if (result.status === 'OK') {
        // Success! Check SuperTokens session and fetch user profile
        const sessionExists = await Session.doesSessionExist()
        if (sessionExists) {
          // Fetch user profile from our backend API
          const profileResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
            credentials: 'include'
          })
          
          console.log('👤 Profile fetch response status:', profileResponse.status)
          
          if (profileResponse.ok) {
            const { user, organization } = await profileResponse.json()
            console.log('🔍 PROOF: User data from DATABASE:', user)
            console.log('🔍 PROOF: Organization data:', organization)
            setAuthState({
              user,
              organization,
              isAuthenticated: true,
              isLoading: false
            })
          } else {
            // Profile fetch failed, but login was successful - set basic state
            console.error('Failed to fetch user profile from /me endpoint')
            setAuthState({
              user: {
                id: result.user?.id || 'unknown',
                email: result.user?.emails?.[0] || credentials.email,
                name: result.user?.emails?.[0] || credentials.email,
                role: 'user'
              },
              organization: null,
              isAuthenticated: true,
              isLoading: false
            })
          }
        }
      } else {
        throw new Error(result.message || 'Login failed')
      }
    } catch (error) {
      console.error('❌ Login error details:', error)
      if (error instanceof Error) {
        console.error('❌ Error message:', error.message)
      }
      throw error
    }
  }

  const signup = async (data: SignupData): Promise<void> => {
    try {
      // Call standard SuperTokens signup endpoint
      const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session
        body: JSON.stringify({
          formFields: [
            { id: "email", value: data.email },
            { id: "password", value: data.password },
            { id: "firstName", value: data.firstName },
            { id: "lastName", value: data.lastName }
          ]
        })
      })

      const result = await response.json()

      if (result.status === 'OK') {
        // Success! Check SuperTokens session and set auth state
        const sessionExists = await Session.doesSessionExist()
        if (sessionExists) {
          // Set basic auth state for new user
          setAuthState({
            user: {
              id: result.user.id,
              email: result.user.email,
              name: result.user.name,
              role: 'user'
            },
            organization: null, // New user won't have organization profile yet
            isAuthenticated: true,
            isLoading: false
          })
        }
      } else {
        throw new Error(result.message || 'Signup failed')
      }
    } catch (error) {
      console.error('Signup error:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await Session.signOut()
      setAuthState({
        user: null,
        organization: null,
        isAuthenticated: false,
        isLoading: false
      })
    } catch (error) {
      console.error('Error during logout:', error)
    }
  }

  const updateUser = async (user: User) => {
    // Update user state and optionally refetch from backend
    setAuthState(prev => ({ ...prev, user }))
  }

  return (
    <AuthContext.Provider 
      value={{
        ...authState,
        login,
        signup,
        logout,
        updateUser
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// Hook moved to separate export to fix Vite Fast Refresh
const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export { useAuth }

// Mock data exports REMOVED to fix Vite Fast Refresh
// export { mockUsers, mockOrganizations }
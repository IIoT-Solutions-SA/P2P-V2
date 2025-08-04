/**
 * Authentication Context
 * 
 * Current Status: Mock implementation for Phase 0.5 testing
 * TODO Phase 2: Replace with SuperTokens integration
 * 
 * SuperTokens integration will include:
 * - Session management
 * - Token refresh
 * - Secure authentication flow
 * - Organization-based signup
 */
import React, { createContext, useContext, useState, useEffect } from 'react'
import type { User, Organization, AuthState, LoginCredentials, SignupData } from '@/types/auth'
import { api } from '@/services'

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
  // Future SuperTokens methods
  refreshSession?: () => Promise<void>
  checkSession?: () => Promise<boolean>
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
    // Check for stored auth state on app load
    const checkAuthState = () => {
      try {
        const storedUser = localStorage.getItem('p2p_user')
        const storedOrg = localStorage.getItem('p2p_organization')
        
        if (storedUser && storedOrg) {
          const user = JSON.parse(storedUser)
          const organization = JSON.parse(storedOrg)
          
          setAuthState({
            user,
            organization,
            isAuthenticated: true,
            isLoading: false
          })
        } else {
          setAuthState(prev => ({ ...prev, isLoading: false }))
        }
      } catch (error) {
        console.error('Error checking auth state:', error)
        setAuthState(prev => ({ ...prev, isLoading: false }))
      }
    }

    // Simulate loading delay
    setTimeout(checkAuthState, 1000)
  }, [])

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Find user by email
      const user = mockUsers.find(u => u.email === credentials.email)
      if (!user) {
        throw new Error('Invalid email or password')
      }

      // Simple password validation (in real app, this would be done on server)
      if (credentials.password !== 'password123') {
        throw new Error('Invalid email or password')
      }

      // Find organization
      const organization = mockOrganizations.find(org => org.id === user.organizationId)
      if (!organization) {
        throw new Error('Organization not found')
      }

      // Update user's last login
      user.lastLogin = new Date()

      // Store auth state
      localStorage.setItem('p2p_user', JSON.stringify(user))
      localStorage.setItem('p2p_organization', JSON.stringify(organization))

      setAuthState({
        user,
        organization,
        isAuthenticated: true,
        isLoading: false
      })
    } catch (error) {
      throw error
    }
  }

  const signup = async (data: SignupData): Promise<void> => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Check if email already exists
      const existingUser = mockUsers.find(u => u.email === data.email)
      if (existingUser) {
        throw new Error('Email already registered')
      }

      // Create new organization
      const newOrganization: Organization = {
        id: `org-${Date.now()}`,
        name: data.organizationName,
        domain: data.email.split('@')[1],
        industry: data.industry,
        size: data.organizationSize as any,
        country: data.country,
        city: data.city,
        isActive: true,
        createdAt: new Date(),
        adminUserId: `user-${Date.now()}`
      }

      // Create new user
      const newUser: User = {
        id: newOrganization.adminUserId,
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        role: 'admin',
        organizationId: newOrganization.id,
        isActive: true,
        lastLogin: new Date(),
        createdAt: new Date()
      }

      // Add to mock data
      mockOrganizations.push(newOrganization)
      mockUsers.push(newUser)

      // Store auth state
      localStorage.setItem('p2p_user', JSON.stringify(newUser))
      localStorage.setItem('p2p_organization', JSON.stringify(newOrganization))

      setAuthState({
        user: newUser,
        organization: newOrganization,
        isAuthenticated: true,
        isLoading: false
      })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('p2p_user')
    localStorage.removeItem('p2p_organization')
    
    setAuthState({
      user: null,
      organization: null,
      isAuthenticated: false,
      isLoading: false
    })
  }

  const updateUser = (user: User) => {
    localStorage.setItem('p2p_user', JSON.stringify(user))
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

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Export mock data for other components to use
export { mockUsers, mockOrganizations }
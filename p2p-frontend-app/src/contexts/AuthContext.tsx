/**
 * Authentication Context with SuperTokens Integration
 * 
 * Real authentication implementation using SuperTokens
 * Handles session management, login/logout, and user state
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import type { User, Organization, AuthState, LoginCredentials, SignupData } from '@/types/auth'
import { api } from '@/services'
import { 
  signInUser, 
  signUpUser, 
  signOutUser, 
  isAuthenticated, 
  getUserId,
  getAccessTokenPayload,
  refreshSession
} from '@/config/supertokens'

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => Promise<void>
  refreshSession: () => Promise<boolean>
  checkSession: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    organization: null,
    isAuthenticated: false,
    isLoading: true
  })

  /**
   * Fetch user profile from backend
   */
  const fetchUserProfile = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/auth/me')
      
      // Handle the response format from our backend
      if (response.data.status === 'OK') {
        return {
          user: response.data.user,
          organization: response.data.organization
        }
      } else {
        throw new Error('Failed to fetch profile')
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      throw error
    }
  }, [])

  /**
   * Initialize authentication state on mount
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check if user has an active session
        const hasSession = await isAuthenticated()
        
        if (hasSession) {
          try {
            // Try to fetch user profile to verify session is valid
            const profileData = await fetchUserProfile()
            setAuthState({
              user: profileData.user,
              organization: profileData.organization,
              isAuthenticated: true,
              isLoading: false
            })
          } catch (profileError) {
            // If profile fetch fails, try to refresh the session
            console.log('Profile fetch failed, attempting session refresh...')
            const refreshed = await refreshSession()
            
            if (refreshed) {
              try {
                // Try fetching profile again after refresh
                const profileData = await fetchUserProfile()
                setAuthState({
                  user: profileData.user,
                  organization: profileData.organization,
                  isAuthenticated: true,
                  isLoading: false
                })
              } catch (secondError) {
                // Both profile fetch and refresh failed - clear auth
                console.log('Session refresh failed, clearing auth state')
                setAuthState({
                  user: null,
                  organization: null,
                  isAuthenticated: false,
                  isLoading: false
                })
              }
            } else {
              // Refresh failed - clear auth
              setAuthState({
                user: null,
                organization: null,
                isAuthenticated: false,
                isLoading: false
              })
            }
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
        console.error('Auth initialization error:', error)
        setAuthState({
          user: null,
          organization: null,
          isAuthenticated: false,
          isLoading: false
        })
      }
    }

    initAuth()
  }, [fetchUserProfile])

  /**
   * Handle user login
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }))

      // Sign in with SuperTokens
      const result = await signInUser(credentials.email, credentials.password)
      
      if (!result || !result.success) {
        throw new Error(result?.message || 'Login failed')
      }

      // Immediately fetch the user profile after successful login
      try {
        const { user, organization } = await fetchUserProfile()
        setAuthState({
          user,
          organization,
          isAuthenticated: true,
          isLoading: false
        })
      } catch (profileError) {
        // If profile fetch fails, still set authenticated but with minimal data
        console.error('Failed to fetch profile after login:', profileError)
        setAuthState({
          user: {
            id: result.user?.id || '',
            email: credentials.email,
            firstName: '',
            lastName: '',
            role: 'member',
            isActive: true
          },
          organization: null,
          isAuthenticated: true,
          isLoading: false
        })
      }
    } catch (error) {
      setAuthState(prev => ({ ...prev, isLoading: false }))
      throw error
    }
  }, [fetchUserProfile])

  /**
   * Handle user signup
   */
  const signup = useCallback(async (data: SignupData) => {
    try {
      console.log('Signup started with data:', { email: data.email, hasPassword: !!data.password })
      setAuthState(prev => ({ ...prev, isLoading: true }))

      // Pass all signup fields to SuperTokens
      console.log('Calling signUpUser with all fields...')
      const additionalFields = {
        firstName: data.firstName,
        lastName: data.lastName,
        organizationName: data.organizationName,
        organizationSize: data.organizationSize,
        industry: data.industry,
        country: data.country,
        city: data.city
      }
      const result = await signUpUser(data.email, data.password, additionalFields)
      console.log('SignUpUser result:', result)
      
      if (!result || !result.success) {
        throw new Error(result?.message || 'Signup failed')
      }

      // For now, create a basic user object from signup data
      // The profile will be fetched properly on next page load
      setAuthState({
        user: {
          id: result.user?.id || '',
          email: data.email,
          firstName: data.firstName,
          lastName: data.lastName,
          role: 'admin',
          isActive: true
        },
        organization: {
          name: data.organizationName,
          size: data.organizationSize,
          industry: data.industry,
          country: data.country,
          city: data.city
        },
        isAuthenticated: true,
        isLoading: false
      })
      
      // Try to fetch full profile in background (non-blocking)
      setTimeout(async () => {
        try {
          const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/v1/auth/me`, {
            credentials: 'include',
            headers: {
              'Content-Type': 'application/json',
            }
          })
          
          if (response.ok) {
            const profileData = await response.json()
            if (profileData.status === 'OK' && profileData.user) {
              setAuthState(prev => ({
                ...prev,
                user: profileData.user,
                organization: profileData.organization
              }))
            }
          }
        } catch (error) {
          console.log('Background profile fetch failed, using local data')
        }
      }, 1000)
      
    } catch (error) {
      console.error('Signup error:', error)
      setAuthState(prev => ({ ...prev, isLoading: false }))
      throw error
    }
  }, [])

  /**
   * Handle user logout
   */
  const logout = useCallback(async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }))

      // Sign out with SuperTokens
      await signOutUser()
      
      // Clear auth state
      setAuthState({
        user: null,
        organization: null,
        isAuthenticated: false,
        isLoading: false
      })

      // Clear remember me preference
      localStorage.removeItem('rememberMe')
    } catch (error) {
      console.error('Logout error:', error)
      setAuthState(prev => ({ ...prev, isLoading: false }))
      throw error
    }
  }, [])

  /**
   * Update user profile
   */
  const updateUser = useCallback(async (updatedUser: User) => {
    try {
      // Update user profile via backend API
      const response = await api.patch<User>('/api/v1/users/me', updatedUser)
      
      setAuthState(prev => ({
        ...prev,
        user: response.data
      }))
    } catch (error) {
      console.error('Failed to update user:', error)
      throw error
    }
  }, [])

  /**
   * Refresh the session
   */
  const handleRefreshSession = useCallback(async (): Promise<boolean> => {
    try {
      const success = await refreshSession()
      
      if (success) {
        // Re-fetch user profile after session refresh
        const { user, organization } = await fetchUserProfile()
        
        setAuthState({
          user,
          organization,
          isAuthenticated: true,
          isLoading: false
        })
      }
      
      return success
    } catch (error) {
      console.error('Session refresh failed:', error)
      return false
    }
  }, [fetchUserProfile])

  /**
   * Check if session is valid
   */
  const checkSession = useCallback(async (): Promise<boolean> => {
    try {
      return await isAuthenticated()
    } catch (error) {
      console.error('Session check failed:', error)
      return false
    }
  }, [])

  // Set up automatic session refresh every 10 minutes
  useEffect(() => {
    if (!authState.isAuthenticated) return
    
    const interval = setInterval(async () => {
      const success = await handleRefreshSession()
      if (!success) {
        console.log('Session refresh failed, logging out user')
        await logout()
      }
    }, 10 * 60 * 1000) // 10 minutes
    
    return () => clearInterval(interval)
  }, [authState.isAuthenticated, handleRefreshSession, logout])

  const value: AuthContextType = {
    ...authState,
    login,
    signup,
    logout,
    updateUser,
    refreshSession: handleRefreshSession,
    checkSession,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Export for direct access if needed
export { AuthContext }
import React, { createContext, useContext, useState, useEffect } from 'react';
import Session from "supertokens-auth-react/recipe/session";
import type { User, Organization, AuthState, LoginCredentials, SignupData } from '@/types/auth';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (user: User) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    organization: null,
    isAuthenticated: false,
    isLoading: true
  });

  useEffect(() => {
    const checkAuthState = async () => {
      try {
        if (await Session.doesSessionExist()) {
          await fetchProfileAndSetState();
        } else {
          setAuthState({ user: null, organization: null, isAuthenticated: false, isLoading: false });
        }
      } catch (error) {
        console.error('Error checking auth state:', error);
        setAuthState({ user: null, organization: null, isAuthenticated: false, isLoading: false });
      }
    };
    checkAuthState();
  }, []);

  const fetchProfileAndSetState = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        credentials: 'include'
      });
      if (response.ok) {
        const { user, organization } = await response.json();
        setAuthState({ user, organization, isAuthenticated: true, isLoading: false });
      } else {
        throw new Error('Failed to fetch user profile.');
      }
    } catch (error) {
      console.error("Profile fetch failed:", error);
      await Session.signOut();
      setAuthState({ user: null, organization: null, isAuthenticated: false, isLoading: false });
    }
  };

  const login = async (credentials: LoginCredentials): Promise<void> => {
    const response = await fetch('http://localhost:8000/api/v1/auth/custom-signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(credentials)
    });

    const result = await response.json();
    if (result.status === 'OK') {
      await fetchProfileAndSetState();
    } else {
      throw new Error(result.message || 'Login failed');
    }
  };

  const signup = async (data: SignupData): Promise<void> => {
    const payload = {
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        password: data.password,
        title: data.title,
        companyName: data.organizationName,
        industrySector: data.industry,
        companySize: data.organizationSize,
        city: data.city
    };
    
    // --- FINAL FIX APPLIED HERE ---
    // STEP 1: Call the custom signup endpoint to create the user.
    const signupResponse = await fetch('http://localhost:8000/api/v1/auth/custom-signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload)
    });

    const signupResult = await signupResponse.json();

    if (signupResult.status === 'OK') {
        // STEP 2: If user creation was successful, immediately call login to create the session.
        await login({ email: data.email, password: data.password });
    } else {
        throw new Error(signupResult.message || 'Signup failed');
    }
  };

  const logout = async () => {
    await Session.signOut();
    setAuthState({
      user: null,
      organization: null,
      isAuthenticated: false,
      isLoading: false
    });
  };

  const updateUser = async (user: User) => {
    setAuthState(prev => ({ ...prev, user }));
  };

  return (
    <AuthContext.Provider 
      value={{ ...authState, login, signup, logout, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

import React, { createContext, useContext, useState, useEffect } from 'react';
import Session from "supertokens-auth-react/recipe/session";
import type { User, AuthState, LoginCredentials, SignupData } from '@/types/auth';
import { ApiError } from '@/lib/api/client';
import { authApi } from '@/lib/api/auth';
import type { MfaRequiredResponse, OtpErrorResponse, SigninResponse } from '@/lib/api/types';
import { useSessionTimeout } from '@/hooks/useSessionTimeout';

export interface MfaChallenge {
  mfaRequired: true;
  challengeId: string;
  email: string;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<MfaChallenge | void>;
  signup: (data: SignupData) => Promise<{ requiresOTPVerification?: boolean; requiresEmailVerification?: boolean; email?: string } | void>;
  logout: () => Promise<void>;
  updateUser: (user: User) => void;
  refreshProfile: () => Promise<void>;
  fetchProfile: () => Promise<void>;
  verifyLoginOtp: (email: string, challengeId: string, code: string) => Promise<void>;
  resendOtp: (email: string, purpose: 'signup_verify' | 'login_mfa') => Promise<{ retryAfterSeconds?: number }>;
}

interface OtpVerificationException extends Error {
  status?: string;
  attemptsRemaining?: number;
}

const isMfaRequiredResponse = (result: SigninResponse): result is MfaRequiredResponse => {
  return result.status === 'MFA_REQUIRED';
};

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
      const { user, organization } = await authApi.me();
      setAuthState({ user, organization, isAuthenticated: true, isLoading: false });
    } catch (error) {
      console.error("Profile fetch failed:", error);
      await Session.signOut();
      setAuthState({ user: null, organization: null, isAuthenticated: false, isLoading: false });
    }
  };

  /**
   * Login with email + password.
   *
   * Returns MfaChallenge if the device is new (OTP required).
   * Returns void (and sets auth state) if the device is trusted.
   */
  const login = async (credentials: LoginCredentials): Promise<MfaChallenge | void> => {
    const result = await authApi.signin(credentials);

    if (result.status === 'OK') {
      // Trusted device — session created, fetch profile
      await fetchProfileAndSetState();
      return;
    }

    if (isMfaRequiredResponse(result)) {
      // New device — caller must redirect to OTP page
      return {
        mfaRequired: true,
        challengeId: result.challengeId,
        email: result.email || credentials.email
      };
    }

    throw new Error(result.message || 'Login failed');
  };

  /**
   * Verify the login MFA OTP and create a session.
   * On success, fetches profile and sets auth state.
   */
  const verifyLoginOtp = async (email: string, challengeId: string, code: string): Promise<void> => {
    let result: OtpErrorResponse;
    try {
      result = await authApi.verifyLoginOtp(email, challengeId, code);
    } catch (error) {
      if (error instanceof ApiError && error.payload && typeof error.payload === 'object') {
        result = error.payload as OtpErrorResponse;
      } else {
        throw error;
      }
    }

    if (result.status === 'OK') {
      await fetchProfileAndSetState();
      return;
    }

    // Propagate structured errors for the OTP page to display
    const err: OtpVerificationException = new Error(result.message || 'OTP verification failed');
    err.status = result.status;
    err.attemptsRemaining = result.attemptsRemaining;
    throw err;
  };

  /**
   * Request a new OTP code (signup_verify or login_mfa).
   */
  const resendOtp = async (email: string, purpose: 'signup_verify' | 'login_mfa'): Promise<{ retryAfterSeconds?: number }> => {
    let result: OtpErrorResponse;
    try {
      result = await authApi.resendOtp(email, purpose);
    } catch (error) {
      if (error instanceof ApiError && error.payload && typeof error.payload === 'object') {
        result = error.payload as OtpErrorResponse;
      } else {
        throw error;
      }
    }

    if (result.status === 'OK') return {};
    if (result.status === 'RATE_LIMITED') return { retryAfterSeconds: result.retryAfterSeconds };
    throw new Error(result.message || 'Failed to resend code');
  };

  /**
   * Signup: admin or member (via invite token).
   *
   * Admin path → returns { requiresOTPVerification: true, email }.
   * Member path → session is created server-side; fetches profile then returns void.
   */
  const signup = async (data: SignupData): Promise<{ requiresOTPVerification?: boolean; requiresEmailVerification?: boolean; email?: string } | void> => {
    const signupResult = await authApi.signup(data);

    if (signupResult.status === 'OK') {
      if (signupResult.requiresOTPVerification) {
        // Admin signup — redirect to OTP verification page
        return {
          requiresOTPVerification: true,
          email: signupResult.email || data.email
        };
      }

      // Member signup — session was created server-side
      await fetchProfileAndSetState();
      return { requiresEmailVerification: false };
    }

    throw new Error(signupResult.message || 'Signup failed');
  };

  const logout = async () => {
    try {
      await authApi.signout();
    } catch (e) {
      console.error('Failed to clear trusted device cookie', e);
    }
    await Session.signOut();
    setAuthState({
      user: null,
      organization: null,
      isAuthenticated: false,
      isLoading: false
    });
  };

  const recordAuthenticatedActivity = async () => {
    try {
      await authApi.sessionActivity();
    } catch (error) {
      // A temporary network failure must not sign the user out. If SuperTokens
      // has cleared an expired/revoked session, synchronize the local auth state.
      if (!(await Session.doesSessionExist())) {
        await logout();
        return;
      }
      console.warn('Session activity heartbeat failed', error);
    }
  };

  useSessionTimeout(authState.isAuthenticated, logout, recordAuthenticatedActivity);

  const updateUser = (user: User) => {
    setAuthState(prev => ({ ...prev, user }));
  };

  const refreshProfile = async () => {
    await fetchProfileAndSetState();
  };

  // Expose fetchProfile as a stable reference for OtpVerification
  const fetchProfile = fetchProfileAndSetState;

  return (
    <AuthContext.Provider
      value={{ ...authState, login, signup, logout, updateUser, refreshProfile, fetchProfile, verifyLoginOtp, resendOtp }}
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

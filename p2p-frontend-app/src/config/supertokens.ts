/**
 * SuperTokens Configuration
 * 
 * Configures SuperTokens for the P2P Sandbox frontend
 * Handles EmailPassword authentication and session management
 */

import SuperTokens from 'supertokens-auth-react';
import EmailPassword from 'supertokens-auth-react/recipe/emailpassword';
import Session from 'supertokens-auth-react/recipe/session';

// Get API domain from environment variables
const API_DOMAIN = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const WEBSITE_DOMAIN = import.meta.env.VITE_WEBSITE_DOMAIN || 'http://localhost:5173';

export function initSuperTokens() {
  SuperTokens.init({
    appInfo: {
      // Your app's name
      appName: "P2P Sandbox",
      // API domain (backend)
      apiDomain: API_DOMAIN,
      // Website domain (frontend)
      websiteDomain: WEBSITE_DOMAIN,
      // API base path for auth endpoints
      apiBasePath: "/auth",
      // Website base path for auth UI (we'll use custom UI)
      websiteBasePath: "/auth"
    },
    recipeList: [
      // Basic EmailPassword Recipe (no custom overrides)
      EmailPassword.init(),
      
      // Basic Session Recipe (no custom overrides)
      Session.init(),
    ],
    // Global configuration
    // Custom UI will be used instead of pre-built UI
    disableAuthRoute: true,
  });
}

// Helper functions for authentication operations

/**
 * Sign up a new user with organization context
 */
export async function signUpUser(
  email: string,
  password: string,
  additionalFields?: Record<string, string>
) {
  try {
    console.log('SuperTokens signUp called with:', { email, hasPassword: !!password, additionalFields })
    console.log('SuperTokens config - apiDomain:', API_DOMAIN)
    console.log('SuperTokens config - websiteDomain:', WEBSITE_DOMAIN)
    
    // Build form fields array with all signup data
    const formFields = [
      { id: "email", value: email },
      { id: "password", value: password },
    ];
    
    // Add additional fields if provided
    if (additionalFields) {
      Object.entries(additionalFields).forEach(([key, value]) => {
        if (value) {
          formFields.push({ id: key, value });
        }
      });
    }
    
    const response = await EmailPassword.signUp({
      formFields,
    });
    console.log('SuperTokens signUp response:', response)

    if (response.status === "FIELD_ERROR") {
      // Handle field errors
      console.log('SuperTokens FIELD_ERROR:', response.formFields)
      return {
        success: false,
        errors: response.formFields,
      };
    } else if (response.status === "SIGN_UP_NOT_ALLOWED") {
      // Handle sign up not allowed
      console.log('SuperTokens SIGN_UP_NOT_ALLOWED:', response.reason)
      return {
        success: false,
        message: response.reason,
      };
    } else if (response.status === "OK") {
      // Sign up successful
      console.log('SuperTokens signup SUCCESS:', response.user)
      return {
        success: true,
        user: response.user,
      };
    } else {
      // Handle unexpected status
      console.log('SuperTokens UNEXPECTED STATUS:', response.status, response)
      return {
        success: false,
        message: `Unexpected status: ${response.status}`,
      };
    }
  } catch (error) {
    console.error("SuperTokens sign up error:", error);
    return {
      success: false,
      message: "An error occurred during sign up",
    };
  }
}

/**
 * Sign in an existing user
 */
export async function signInUser(email: string, password: string) {
  try {
    const response = await EmailPassword.signIn({
      formFields: [
        { id: "email", value: email },
        { id: "password", value: password },
      ],
    });

    if (response.status === "FIELD_ERROR") {
      // Handle field errors
      return {
        success: false,
        errors: response.formFields,
      };
    } else if (response.status === "WRONG_CREDENTIALS_ERROR") {
      // Handle wrong credentials
      return {
        success: false,
        message: "Invalid email or password",
      };
    } else if (response.status === "SIGN_IN_NOT_ALLOWED") {
      // Handle sign in not allowed
      return {
        success: false,
        message: response.reason,
      };
    } else if (response.status === "OK") {
      // Sign in successful
      return {
        success: true,
        user: response.user,
      };
    }
  } catch (error) {
    console.error("Sign in error:", error);
    return {
      success: false,
      message: "An error occurred during sign in",
    };
  }
}

/**
 * Sign out the current user
 */
export async function signOutUser() {
  try {
    await Session.signOut();
    return { success: true };
  } catch (error) {
    console.error("Sign out error:", error);
    return {
      success: false,
      message: "An error occurred during sign out",
    };
  }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  return await Session.doesSessionExist();
}

/**
 * Get current user ID from session
 */
export async function getUserId(): Promise<string | undefined> {
  if (await Session.doesSessionExist()) {
    const userId = await Session.getUserId();
    return userId;
  }
  return undefined;
}

/**
 * Get access token payload
 */
export async function getAccessTokenPayload(): Promise<any> {
  if (await Session.doesSessionExist()) {
    const payload = await Session.getAccessTokenPayloadSecurely();
    return payload;
  }
  return null;
}

/**
 * Refresh the session
 */
export async function refreshSession(): Promise<boolean> {
  try {
    const response = await Session.attemptRefreshingSession();
    return response;
  } catch (error) {
    console.error("Failed to refresh session:", error);
    return false;
  }
}

// Export Session for direct access if needed
export { Session };
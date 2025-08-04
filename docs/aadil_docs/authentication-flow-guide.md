# Authentication Flow Guide for P2P Sandbox

## Overview
This guide details the complete authentication flow for the P2P Sandbox platform, covering SuperTokens integration, session management, and security best practices for both frontend and backend.

## Table of Contents
1. [Authentication Architecture](#authentication-architecture)
2. [SuperTokens Setup](#supertokens-setup)
3. [User Registration Flow](#user-registration-flow)
4. [Login Flow](#login-flow)
5. [Session Management](#session-management)
6. [Password Reset Flow](#password-reset-flow)
7. [Email Verification](#email-verification)
8. [Role-Based Access Control](#role-based-access-control)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)

## Authentication Architecture

### System Components

1. **Frontend (React)**
   - SuperTokens Auth React SDK
   - Session management
   - Protected routes
   - Auth UI components

2. **Backend (FastAPI)**
   - SuperTokens Python SDK
   - Session validation
   - User management
   - Token handling

3. **SuperTokens Core**
   - Session storage
   - Token generation
   - Refresh logic
   - Security features

4. **Databases**
   - PostgreSQL: User and organization data
   - SuperTokens DB: Session information

### Architecture Flow

```
Frontend <-> Backend API <-> SuperTokens Core
              |                    |
              v                    v
         PostgreSQL          SuperTokens DB
```

## SuperTokens Setup

### Backend Configuration

1. **Installation Requirements**
   - SuperTokens Python SDK
   - PostgreSQL for SuperTokens Core
   - Environment variables configuration

2. **Initialization Steps**
   - Configure connection URI
   - Set up recipe configuration
   - Initialize middleware
   - Configure CORS properly

3. **Recipe Configuration**
   - EmailPassword recipe for authentication
   - Session recipe for session management
   - Custom callbacks for user creation

### Frontend Configuration

1. **SDK Installation**
   - Install supertokens-auth-react
   - Configure React app wrapper
   - Set up routing integration

2. **Initialization**
   - Configure app info
   - Set API endpoints
   - Configure UI options
   - Handle redirects

3. **Session Configuration**
   - Cookie settings
   - Refresh mechanism
   - Anti-CSRF setup

## User Registration Flow

### Process Overview

1. **User Initiates Signup**
   - Fills organization details
   - Provides user information
   - Submits credentials

2. **Frontend Validation**
   - Validate email format
   - Check password strength
   - Verify required fields

3. **Backend Processing**
   ```
   1. Receive signup request
   2. Validate input data
   3. Check email uniqueness
   4. Create organization record
   5. Create SuperTokens user
   6. Create application user
   7. Link user to organization
   8. Send verification email
   9. Return success response
   ```

4. **Session Creation**
   - Generate session tokens
   - Set secure cookies
   - Return user data

### Special Considerations

- **Organization Creation**
  - Admin user created with organization
  - Domain extracted from email
  - Industry and size captured

- **Error Scenarios**
  - Email already exists
  - Invalid organization data
  - Database constraints
  - SuperTokens errors

### Data Flow

```
Frontend Form -> API Endpoint -> Validation
                                    |
                                    v
                            Organization Creation
                                    |
                                    v
                            SuperTokens User
                                    |
                                    v
                            Application User
                                    |
                                    v
                            Session + Response
```

## Login Flow

### Standard Login Process

1. **User Submits Credentials**
   - Email and password
   - Optional "remember me"

2. **Backend Validation**
   ```
   1. Verify credentials with SuperTokens
   2. Load user from database
   3. Check user status (active, verified)
   4. Load organization data
   5. Create session
   6. Return user + organization
   ```

3. **Frontend Updates**
   - Store session
   - Update auth context
   - Redirect to dashboard

### Session Token Flow

1. **Access Token**
   - Short-lived (15 minutes)
   - Used for API requests
   - Stored in memory

2. **Refresh Token**
   - Long-lived (3 months)
   - Stored in httpOnly cookie
   - Used to refresh access token

### Multi-Device Support

- Sessions tracked per device
- Logout options (current/all devices)
- Device management interface

## Session Management

### Automatic Session Refresh

1. **Token Expiry Detection**
   - Frontend detects 401 response
   - Automatically attempts refresh
   - Retry original request

2. **Refresh Process**
   - Use refresh token
   - Get new access token
   - Update session
   - Continue operation

3. **Refresh Failure**
   - Clear local session
   - Redirect to login
   - Show appropriate message

### Session Persistence

1. **Browser Refresh**
   - Session survives refresh
   - Cookies maintain state
   - Quick validation on load

2. **Tab Synchronization**
   - Sessions sync across tabs
   - Logout affects all tabs
   - Real-time updates

### Session Security

- **HttpOnly Cookies**: Prevent XSS attacks
- **Secure Flag**: HTTPS only in production
- **SameSite**: CSRF protection
- **Anti-CSRF Tokens**: Additional protection

## Password Reset Flow

### Reset Request Process

1. **User Requests Reset**
   - Enter email address
   - Submit request

2. **Backend Processing**
   ```
   1. Validate email exists
   2. Generate reset token
   3. Store token with expiry
   4. Send email with link
   5. Return success (always)
   ```

3. **Email Security**
   - Don't reveal email existence
   - Time-limited tokens
   - Single-use tokens

### Password Update Process

1. **User Clicks Reset Link**
   - Validate token
   - Show password form

2. **New Password Submission**
   - Validate password strength
   - Verify token again
   - Update password
   - Invalidate all sessions
   - Auto-login optional

### Security Measures

- Token expiry (1 hour)
- Rate limiting
- Secure token generation
- Audit logging

## Email Verification

### Verification Flow

1. **After Registration**
   - Email sent automatically
   - User can still login
   - Limited features until verified

2. **Verification Link**
   - Contains secure token
   - Links to frontend
   - Frontend calls API

3. **Backend Verification**
   ```
   1. Validate token
   2. Update user status
   3. Grant full access
   4. Log verification
   ```

### Resend Functionality

- Rate limited (1 per minute)
- Maximum attempts tracked
- Alternative verification methods

## Role-Based Access Control

### Role Hierarchy

1. **Organization Admin**
   - Full organization access
   - User management
   - Settings control
   - All features

2. **Organization Member**
   - Standard features
   - Own content management
   - Read access

### Implementation Strategy

1. **Backend Enforcement**
   - Decorator for endpoints
   - Role checking middleware
   - Database constraints

2. **Frontend Protection**
   - Route guards
   - Component visibility
   - API call prevention

### Permission Checking

```
Request -> Auth Middleware -> Role Check -> Endpoint
                                  |
                                  v
                            403 if unauthorized
```

## Security Considerations

### Best Practices

1. **Password Requirements**
   - Minimum 8 characters
   - Complexity requirements
   - Common password blocking
   - Breach database checking

2. **Session Security**
   - Secure cookie settings
   - Regular token rotation
   - IP validation optional
   - Device fingerprinting

3. **Attack Prevention**
   - Rate limiting all endpoints
   - Captcha for public forms
   - Account lockout policies
   - Audit logging

### CORS Configuration

1. **Development**
   - Allow localhost origins
   - Credentials enabled
   - Specific methods/headers

2. **Production**
   - Whitelist specific domains
   - Strict origin checking
   - Minimal exposed headers

### Data Protection

- Hash passwords with bcrypt
- Salt all hashes
- Encrypt sensitive data
- Secure token storage

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check origin configuration
   - Verify credentials setting
   - Inspect preflight requests

2. **Session Not Persisting**
   - Check cookie settings
   - Verify domain configuration
   - Inspect browser storage

3. **401 Errors**
   - Check token expiry
   - Verify refresh mechanism
   - Inspect session validity

4. **Email Not Sending**
   - Check SMTP configuration
   - Verify email templates
   - Check spam folders

### Debug Strategies

1. **Frontend Debugging**
   - Check network requests
   - Inspect cookies
   - Log session state
   - Use React DevTools

2. **Backend Debugging**
   - Log all auth attempts
   - Check SuperTokens logs
   - Verify database state
   - Test with Postman

### Testing Authentication

1. **Manual Testing**
   - Test each flow completely
   - Try edge cases
   - Test error scenarios
   - Verify security measures

2. **Automated Testing**
   - Unit test auth functions
   - Integration test flows
   - E2E test user journeys
   - Security scanning

## Implementation Checklist

- [ ] Install SuperTokens dependencies
- [ ] Configure SuperTokens Core
- [ ] Implement signup with organization
- [ ] Complete login flow
- [ ] Add session management
- [ ] Implement password reset
- [ ] Add email verification
- [ ] Configure role-based access
- [ ] Set up security measures
- [ ] Test all flows thoroughly
- [ ] Document custom configurations
- [ ] Plan monitoring strategy
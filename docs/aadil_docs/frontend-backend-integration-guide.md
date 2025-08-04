# Frontend-Backend Integration Guide for P2P Sandbox

## Overview
This guide provides a comprehensive approach to integrating the React frontend with the FastAPI backend for the P2P Sandbox platform. It covers the essential steps, configurations, and best practices needed for seamless integration.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Frontend Dependencies](#frontend-dependencies)
3. [Environment Configuration](#environment-configuration)
4. [API Client Setup](#api-client-setup)
5. [Authentication Integration](#authentication-integration)
6. [Error Handling Strategy](#error-handling-strategy)
7. [Testing Integration](#testing-integration)
8. [Common Issues and Solutions](#common-issues-and-solutions)

## Prerequisites

Before starting the integration, ensure you have:
- Backend running in Docker containers (port 8000)
- Frontend development server (port 5173)
- SuperTokens service running (port 3567)
- Both PostgreSQL and MongoDB accessible

## Frontend Dependencies

### Required NPM Packages

The frontend needs several key dependencies for backend integration:

1. **axios** (^1.6.0)
   - HTTP client for API calls
   - Supports interceptors for auth tokens
   - Better error handling than fetch

2. **supertokens-auth-react** (^0.35.0)
   - Frontend SDK for SuperTokens authentication
   - Handles session management automatically
   - Provides React components and hooks

3. **@tanstack/react-query** (^5.0.0)
   - Server state management
   - Caching and synchronization
   - Optimistic updates support

4. **socket.io-client** (^4.5.0)
   - WebSocket client for real-time features
   - Automatic reconnection handling
   - Event-based communication

### Installation Steps

1. Navigate to frontend directory
2. Install dependencies using npm or yarn
3. Update TypeScript configurations if needed
4. Verify no version conflicts exist

## Environment Configuration

### Frontend Environment Variables

Create a `.env.development` file in the frontend root:

```
VITE_API_URL=http://localhost:8000/api/v1
VITE_SUPERTOKENS_URL=http://localhost:3567
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
VITE_APP_NAME=P2P Sandbox
```

### Backend CORS Configuration

The backend must allow the frontend origin:

1. Add frontend URL to allowed origins list
2. Enable credentials for cookie-based auth
3. Configure allowed headers and methods
4. Set appropriate max age for preflight

### Development vs Production

- Use environment-specific configuration files
- Implement proper URL resolution
- Handle HTTPS in production
- Configure proxy if needed

## API Client Setup

### Creating the API Service

1. **Base Configuration**
   - Set base URL from environment
   - Configure timeout (30 seconds recommended)
   - Set default headers
   - Enable credentials for cookies

2. **Request Interceptors**
   - Add authentication headers
   - Log requests in development
   - Transform request data if needed
   - Handle request errors

3. **Response Interceptors**
   - Transform response data
   - Handle authentication errors
   - Implement retry logic
   - Log responses in development

### SuperTokens Integration

1. Initialize SuperTokens in the frontend app
2. Add axios interceptors for automatic token handling
3. Configure session refresh mechanism
4. Handle authentication redirects

## Authentication Integration

### Initial Setup

1. **SuperTokens Initialization**
   - Configure app info (name, API domain, website domain)
   - Set up recipe list (EmailPassword, Session)
   - Configure UI components if using pre-built ones

2. **Session Management**
   - Implement session checking on app load
   - Handle session expiry gracefully
   - Set up automatic refresh
   - Configure anti-CSRF if needed

### Authentication Flow

1. **Signup Process**
   - Collect user and organization data
   - Send to backend signup endpoint
   - Handle validation errors
   - Auto-login after successful signup

2. **Login Process**
   - Validate credentials on frontend
   - Send to backend login endpoint
   - Store session information
   - Redirect to dashboard

3. **Logout Process**
   - Call backend logout endpoint
   - Clear local session data
   - Redirect to login page
   - Handle logout errors

### Protected Routes

- Implement route guards
- Check authentication status
- Handle loading states
- Redirect unauthorized users

## Error Handling Strategy

### API Error Types

1. **Network Errors**
   - No internet connection
   - Server unreachable
   - Timeout errors

2. **Authentication Errors**
   - Invalid credentials
   - Session expired
   - Unauthorized access

3. **Validation Errors**
   - Invalid input data
   - Missing required fields
   - Format violations

4. **Server Errors**
   - 500 Internal Server Error
   - 503 Service Unavailable
   - Database connection issues

### Error Response Format

Ensure consistent error format:
```
{
  "message": "Human-readable error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "details": {
    "field": "Specific field error"
  }
}
```

### User-Friendly Error Display

1. Show appropriate error messages
2. Provide actionable feedback
3. Log errors for debugging
4. Implement retry mechanisms

## Testing Integration

### Manual Testing Checklist

1. **Authentication Flow**
   - [ ] Can create new account with organization
   - [ ] Can login with valid credentials
   - [ ] Session persists across page refreshes
   - [ ] Logout clears all session data

2. **API Communication**
   - [ ] GET requests retrieve data correctly
   - [ ] POST requests send data properly
   - [ ] File uploads work as expected
   - [ ] Error responses are handled

3. **Real-time Features**
   - [ ] WebSocket connections establish
   - [ ] Messages are received in real-time
   - [ ] Reconnection works after disconnect
   - [ ] Multiple tabs sync properly

### Automated Testing

1. **Integration Tests**
   - Test complete user flows
   - Mock backend responses
   - Verify error scenarios
   - Check loading states

2. **E2E Tests**
   - Run against real backend
   - Test critical paths
   - Verify data persistence
   - Check cross-browser compatibility

## Common Issues and Solutions

### CORS Issues

**Problem**: Blocked by CORS policy
**Solution**: 
- Verify backend CORS configuration
- Check request credentials setting
- Ensure correct origin is allowed
- Use proxy in development if needed

### Authentication Failures

**Problem**: Session not persisting
**Solution**:
- Check cookie settings
- Verify domain configuration
- Ensure HTTPS in production
- Check SameSite settings

### Network Errors

**Problem**: Cannot reach backend
**Solution**:
- Verify backend is running
- Check Docker container status
- Confirm correct ports
- Test with curl/Postman

### Type Mismatches

**Problem**: TypeScript errors with API responses
**Solution**:
- Update type definitions
- Use type guards
- Implement response transformers
- Consider code generation tools

### Performance Issues

**Problem**: Slow API responses
**Solution**:
- Implement request caching
- Use pagination properly
- Optimize payload size
- Consider request batching

## Best Practices

1. **Security**
   - Never store sensitive data in localStorage
   - Use HTTPS in production
   - Implement proper CSRF protection
   - Validate input on both frontend and backend

2. **Performance**
   - Implement proper caching strategies
   - Use lazy loading for large lists
   - Optimize bundle size
   - Minimize API calls

3. **Developer Experience**
   - Maintain consistent code structure
   - Document API changes
   - Use TypeScript strictly
   - Implement proper logging

4. **User Experience**
   - Show loading states
   - Provide clear error messages
   - Implement optimistic updates
   - Handle offline scenarios

## Next Steps

1. Complete environment setup
2. Install required dependencies
3. Implement authentication flow
4. Test integration thoroughly
5. Document any project-specific configurations
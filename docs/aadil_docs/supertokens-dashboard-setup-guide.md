# SuperTokens Dashboard Setup Guide

## Overview

This document provides comprehensive instructions for setting up the SuperTokens Dashboard for admin user management in the P2P Sandbox project. The dashboard allows administrators to manage users, sessions, and authentication settings through a web interface.

## Dashboard Access Information

### 🔑 Dashboard Credentials
- **Dashboard URL**: http://localhost:8000/auth/dashboard
- **Admin Email**: `admin@test.com`
- **Admin Password**: `password123`
- **User ID**: `c2cfd8d5-b469-41ad-8ae6-b906ef5c7409`
- **Status**: ✅ Active and Functional

### 🌐 Access URLs
- **Production Dashboard**: `{API_DOMAIN}/auth/dashboard`
- **Development Dashboard**: `http://localhost:8000/auth/dashboard`
- **API Base Path**: `/auth` (configured in SuperTokens)

## Implementation Steps Completed

### Step 1: Dashboard Recipe Configuration

**File Modified**: `/p2p-backend-app/app/core/supertokens.py`

```python
# Dashboard Recipe for monitoring and management
dashboard.init(
    # No additional config needed - API key handled by core
),
```

**Key Points**:
- ✅ Dashboard recipe added to SuperTokens initialization
- ✅ No API key required for self-hosted SuperTokens
- ✅ Uses default dashboard configuration

### Step 2: Backend Configuration

**File Modified**: `/p2p-backend-app/app/core/config.py`

```python
SUPERTOKENS_CONNECTION_URI: str = "http://supertokens:3567"
SUPERTOKENS_API_KEY: Optional[str] = None  # Not needed for self-hosted SuperTokens
```

**Key Points**:
- ✅ API key correctly set to `None` for self-hosted setup
- ✅ Connection URI points to SuperTokens container
- ✅ Self-hosted configuration (no managed service API key)

### Step 3: Dashboard Credentials Creation

**Command Used**:
```bash
curl --location --request POST 'http://localhost:3567/recipe/dashboard/user' \
--header 'rid: dashboard' \
--header 'Content-Type: application/json' \
--data-raw '{"email":"admin@test.com","password":"password123"}'
```

**Response**:
```json
{
  "status": "OK",
  "user": {
    "email": "admin@test.com",
    "userId": "c2cfd8d5-b469-41ad-8ae6-b906ef5c7409",
    "timeJoined": 1754738491409
  }
}
```

## Dashboard Features Available

### 👥 User Management
- View all registered users
- Create new users manually
- Edit user information
- Delete users
- View user registration timestamps

### 🔐 Session Management
- View active user sessions
- Invalidate specific sessions
- Monitor session activity
- Session timeout management

### ✉️ Email Verification
- View email verification status
- Send verification emails
- Mark emails as verified manually
- Manage verification flows

### 📊 User Analytics
- Registration statistics
- Login activity tracking
- User engagement metrics
- Session duration analytics

### 🏢 Organization Management
- View user organization associations
- Manage multi-tenant configurations
- Organization-specific user filtering

## Critical Configuration Notes

### ✅ What Was Done Correctly

1. **Self-Hosted Setup**: No API key required or configured
2. **Dashboard Recipe**: Properly initialized without custom configuration
3. **Credential Creation**: Used direct SuperTokens core API
4. **URL Structure**: Dashboard accessible at correct API domain path

### ⚠️ Important Things to Avoid

#### 1. **Never Add API Key for Self-Hosted**
```python
# ❌ WRONG - Don't do this for self-hosted
dashboard.init(
    api_key="some-random-key"
),

# ✅ CORRECT - Simple initialization
dashboard.init(),
```

#### 2. **Never Use Managed Service Commands**
```bash
# ❌ WRONG - This is for managed service
curl -H "api-key: managed-service-key" ...

# ✅ CORRECT - No API key for self-hosted
curl --header 'rid: dashboard' ...
```

#### 3. **Never Access Wrong URL Path**
```
❌ WRONG URLs:
- http://localhost:3567/dashboard (SuperTokens core direct)
- http://localhost:5173/auth/dashboard (Frontend domain)

✅ CORRECT URL:
- http://localhost:8000/auth/dashboard (API domain)
```

#### 4. **Never Skip Required Headers**
```bash
# ❌ WRONG - Missing rid header
curl -X POST 'http://localhost:3567/recipe/dashboard/user' \
--data-raw '{"email":"admin@test.com","password":"password"}'

# ✅ CORRECT - Include rid header
curl -X POST 'http://localhost:3567/recipe/dashboard/user' \
--header 'rid: dashboard' \
--data-raw '{"email":"admin@test.com","password":"password"}'
```

## Troubleshooting Common Issues

### Issue 1: "Invalid Json Input"
**Cause**: Missing `rid: dashboard` header or malformed JSON
**Solution**: Always include the `rid: dashboard` header in credential creation requests

### Issue 2: "Not Found" on Dashboard URL
**Cause**: Dashboard recipe not initialized in backend
**Solution**: Ensure `dashboard.init()` is in the SuperTokens recipes list

### Issue 3: "API Key Required" Error
**Cause**: Trying to use managed service commands on self-hosted
**Solution**: Remove all API key references for self-hosted setup

### Issue 4: Dashboard Loads But Can't Login
**Cause**: Dashboard credentials not created properly
**Solution**: Re-create credentials using the exact curl command format

## Security Considerations

### 🔒 Production Security
- **Change Default Password**: Replace `password123` with strong password
- **Use Strong Email**: Replace `admin@test.com` with organization email
- **Network Security**: Restrict dashboard access to admin networks only
- **HTTPS**: Always use HTTPS in production for dashboard access

### 🛡️ Access Control
- **Admin Restrictions**: Use `admins` array to restrict write operations
- **Read-Only Users**: Configure non-admin dashboard users for monitoring
- **Session Timeout**: Configure appropriate session timeouts for admin users

## Maintenance

### Regular Tasks
1. **Monitor Dashboard Access**: Review admin login activity
2. **Update Credentials**: Rotate dashboard passwords periodically
3. **User Cleanup**: Remove inactive or test users
4. **Session Management**: Monitor and clean up stale sessions

### Backup Considerations
- Dashboard users are stored in SuperTokens core database
- Include SuperTokens database in backup procedures
- Document admin credentials securely

## Additional Admin Users

To create additional dashboard users:

```bash
curl --location --request POST 'http://localhost:3567/recipe/dashboard/user' \
--header 'rid: dashboard' \
--header 'Content-Type: application/json' \
--data-raw '{"email":"ADMIN_EMAIL","password":"ADMIN_PASSWORD"}'
```

## Integration with P2P Sandbox

The dashboard integrates seamlessly with the P2P Sandbox authentication system:

- **User Visibility**: All P2P Sandbox users appear in the dashboard
- **Session Management**: Can manage P2P application sessions
- **Organization Context**: View users within their organization context
- **Real-time Updates**: Changes reflect immediately in the application

## Version Information

- **SuperTokens Version**: 11.0.5
- **Dashboard Version**: 0.13
- **Setup Date**: August 9, 2025
- **Last Updated**: August 9, 2025

---

**Status**: ✅ **Fully Operational**  
**Next Review Date**: September 9, 2025  
**Maintained By**: Development Team
# Authentication UI Testing Plan

## Overview
This comprehensive plan guides you through testing the complete authentication system via the frontend UI, verifying all operations work correctly and changes are reflected in databases and the SuperTokens dashboard.

---

## Prerequisites Checklist

### 1. Backend Services Running
Ensure all Docker services are up:
```bash
cd /mnt/d/Projects/P2P-V2/p2p-backend-app
docker-compose ps
```

All services should show "Up":
- postgres (Port 5432)
- mongodb (Port 27017)
- redis (Port 6379)
- supertokens (Port 3567)
- backend (Port 8000)

### 2. Backend Health Check
Verify backend is healthy:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

### 3. Environment Files Setup
Ensure both .env files exist and are configured:

**Backend .env** (`p2p-backend-app/.env`):
```env
DATABASE_URL=postgresql+asyncpg://p2p_user:p2p_password@localhost:5432/p2p_sandbox
MONGODB_URL=mongodb://localhost:27017
SUPERTOKENS_CONNECTION_URI=http://localhost:3567
SUPERTOKENS_API_KEY=your-supertokens-api-key
SUPERTOKENS_API_DOMAIN=http://localhost:8000
SUPERTOKENS_WEBSITE_DOMAIN=http://localhost:5173
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**Frontend .env** (`p2p-frontend-app/.env`):
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPERTOKENS_API_DOMAIN=http://localhost:8000
VITE_SUPERTOKENS_API_BASE_PATH=/auth
VITE_WEBSITE_DOMAIN=http://localhost:5173
```

---

## Part 1: Frontend Startup

### Step 1: Install Dependencies
```bash
cd /mnt/d/Projects/P2P-V2/p2p-frontend-app
npm install
```

### Step 2: Start Frontend Dev Server
```bash
npm run dev
```

Expected output:
```
VITE v5.0.x ready in XXX ms
➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### Step 3: Open Application
1. Open browser (Chrome recommended for DevTools)
2. Navigate to: http://localhost:5173
3. Open Developer Tools (F12)
4. Go to Network tab to monitor API calls
5. Keep Console tab visible for errors

---

## Part 2: Testing User Registration (Signup)

### Test Case 1: Successful Organization Signup

**Steps:**
1. Click "Get Started" or navigate to signup page
2. Fill in the form:
   - Email: `admin@testcompany.com`
   - Password: `TestPassword123!`
   - First Name: `John`
   - Last Name: `Doe`
   - Organization Name: `Test Company Inc`
   - Organization Size: `Medium (11-50 employees)`
   - Industry: `Technology`
   - City: `Riyadh`
3. Click "Sign Up"

**Expected Results:**
- Loading indicator appears
- Network tab shows:
  - POST to `/auth/signup` (200 OK)
  - POST to `/auth/emailpassword/signup` (200 OK)
  - POST to `/auth/session/refresh` (200 OK)
- User is redirected to dashboard
- User info appears in header

**Database Verification:**
```sql
-- Check PostgreSQL for user and organization
psql -h localhost -U p2p_user -d p2p_sandbox

-- Check organizations table
SELECT * FROM organizations WHERE email = 'admin@testcompany.com';

-- Check users table  
SELECT * FROM users WHERE email = 'admin@testcompany.com';

-- Verify user is admin
SELECT u.email, u.role, u.status, o.name as org_name 
FROM users u 
JOIN organizations o ON u.organization_id = o.id 
WHERE u.email = 'admin@testcompany.com';
```

### Test Case 2: Duplicate Email Registration

**Steps:**
1. Try to sign up with same email again
2. Use different organization name

**Expected Results:**
- Error message: "User with this email already exists"
- No new records in database
- User remains on signup page

### Test Case 3: Invalid Data Validation

**Test these scenarios:**
- Password less than 8 characters
- Invalid email format
- Empty required fields
- Invalid organization size value

**Expected Results:**
- Form validation errors appear
- No API calls made until validation passes

---

## Part 3: Testing User Login

### Test Case 4: Successful Login

**Steps:**
1. If logged in, click "Logout" first
2. Navigate to login page
3. Enter credentials:
   - Email: `admin@testcompany.com`
   - Password: `TestPassword123!`
4. Click "Sign In"

**Expected Results:**
- Network tab shows:
  - POST to `/auth/signin` (200 OK)
  - POST to `/auth/emailpassword/signin` (200 OK)
  - GET to `/api/v1/users/me` (200 OK)
- User redirected to dashboard
- User profile loaded in header
- Session cookie set (check Application > Cookies)

**Session Verification:**
```javascript
// In browser console
localStorage.getItem('supertokens-auth-session')
document.cookie
```

### Test Case 5: Invalid Credentials

**Test scenarios:**
1. Wrong password
2. Non-existent email
3. Empty fields

**Expected Results:**
- Error message: "Invalid email or password"
- User remains on login page
- No session created

---

## Part 4: Testing Session Management

### Test Case 6: Session Persistence

**Steps:**
1. After successful login, refresh the page (F5)
2. Close browser tab and reopen
3. Navigate directly to http://localhost:5173/dashboard

**Expected Results:**
- User remains logged in
- Session automatically refreshes
- No redirect to login page

### Test Case 7: Session Expiry (Optional - Long Test)

**Steps:**
1. Login successfully
2. Wait for session to expire (default: 1 hour)
3. Try to access protected page

**Expected Results:**
- Automatic token refresh attempt
- If refresh fails, redirect to login

---

## Part 5: Testing Logout

### Test Case 8: Successful Logout

**Steps:**
1. While logged in, click user menu
2. Click "Logout"

**Expected Results:**
- Network tab shows:
  - POST to `/auth/signout` (200 OK)
- Session cleared from storage
- Redirect to home/login page
- Cannot access protected pages

**Verification:**
```javascript
// In browser console after logout
localStorage.getItem('supertokens-auth-session') // Should be null
```

---

## Part 6: SuperTokens Dashboard Verification

### Access SuperTokens Dashboard

**Steps:**
1. Open new browser tab
2. Navigate to: http://localhost:3567/dashboard
3. If prompted for API key, enter: `your-supertokens-api-key`

**What to Check:**
1. **Users Section:**
   - See registered user `admin@testcompany.com`
   - Check user ID matches database
   - View user metadata

2. **Sessions Section:**
   - Active sessions for logged-in users
   - Session creation/expiry times
   - Session tokens

3. **Analytics:**
   - Number of signups
   - Active users
   - Failed login attempts

---

## Part 7: Protected Routes Testing

### Test Case 9: Accessing Protected Pages

**Test these pages while logged out:**
- `/dashboard`
- `/forum`
- `/use-cases`
- `/settings`

**Expected Results:**
- Redirect to login page
- After login, redirect back to requested page

### Test Case 10: Role-Based Access

**As Admin User:**
1. Navigate to Settings > Users
2. Should see user management options

**As Regular User (if you create one):**
1. Navigate to Settings
2. Should NOT see admin options

---

## Part 8: Database Monitoring

### PostgreSQL Monitoring
```bash
# Connect to database
psql -h localhost -U p2p_user -d p2p_sandbox

# Monitor users table
SELECT id, email, role, status, created_at 
FROM users 
ORDER BY created_at DESC;

# Monitor organizations
SELECT id, name, email, status, created_at 
FROM organizations 
ORDER BY created_at DESC;

# Check user sessions (if stored)
SELECT * FROM user_sessions WHERE user_id = '<user-id>';
```

### MongoDB Monitoring (for future features)
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/p2p_sandbox

# Check collections
show collections

# View any auth-related documents
db.auth_logs.find().sort({created_at: -1}).limit(5)
```

---

## Part 9: Error Scenarios Testing

### Test Case 11: Network Errors

**Steps:**
1. Stop backend: `docker-compose stop backend`
2. Try to login
3. Try to signup

**Expected Results:**
- User-friendly error messages
- No application crash
- Graceful degradation

### Test Case 12: CORS Issues

**Verify CORS is working:**
1. Check browser console for CORS errors
2. All API calls should succeed without CORS blocks

---

## Part 10: Performance Testing

### Check Performance Metrics

**In Chrome DevTools:**
1. Network tab > check request timings
2. Performance tab > record signup/login flow

**Expected Metrics:**
- Login API: < 500ms
- Signup API: < 1000ms
- Session refresh: < 200ms
- Page load after login: < 2000ms

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "Cannot connect to backend"
```bash
# Check backend is running
docker-compose ps
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

#### 2. "CORS error in browser"
```bash
# Check backend CORS settings
cat p2p-backend-app/.env | grep CORS

# Should include http://localhost:5173
```

#### 3. "SuperTokens connection error"
```bash
# Check SuperTokens is running
docker-compose ps supertokens
docker-compose logs supertokens

# Test SuperTokens directly
curl http://localhost:3567/hello
```

#### 4. "Database connection error"
```bash
# Check PostgreSQL
docker-compose ps postgres
psql -h localhost -U p2p_user -d p2p_sandbox -c "SELECT 1"

# Check MongoDB
docker-compose ps mongodb
mongosh mongodb://localhost:27017/p2p_sandbox --eval "db.stats()"
```

---

## Test Results Template

Copy this template to track your testing:

```markdown
## Test Execution Report

**Date:** [DATE]
**Tester:** [YOUR NAME]
**Environment:** Development

### Test Summary
- [ ] Part 1: Frontend Startup - PASS/FAIL
- [ ] Part 2: User Registration - PASS/FAIL
- [ ] Part 3: User Login - PASS/FAIL
- [ ] Part 4: Session Management - PASS/FAIL
- [ ] Part 5: Logout - PASS/FAIL
- [ ] Part 6: SuperTokens Dashboard - PASS/FAIL
- [ ] Part 7: Protected Routes - PASS/FAIL
- [ ] Part 8: Database Verification - PASS/FAIL
- [ ] Part 9: Error Scenarios - PASS/FAIL
- [ ] Part 10: Performance - PASS/FAIL

### Issues Found
1. [Issue description]
   - Steps to reproduce
   - Expected vs Actual
   - Screenshot/Error message

### Notes
[Any additional observations]
```

---

## Success Criteria

Your authentication system is working correctly if:

✅ Users can sign up with organization creation
✅ Users can login with correct credentials
✅ Sessions persist across page refreshes
✅ Logout clears session completely
✅ Protected routes redirect when not authenticated
✅ Database shows correct user/org records
✅ SuperTokens dashboard shows user activity
✅ No CORS or network errors
✅ All API responses return expected data
✅ Performance is acceptable (< 1s for most operations)

---

## Next Steps After Testing

Once all tests pass:

1. **Document any issues** found during testing
2. **Create bug reports** for any failures
3. **Performance optimization** if any slow operations
4. **Security review** of authentication flow
5. **Move to Phase 4** - Forum System Implementation

---

## Additional Testing Resources

### Browser DevTools Shortcuts
- F12: Open DevTools
- Ctrl+Shift+I: Inspect element
- Ctrl+Shift+J: Console
- Ctrl+Shift+C: Select element
- Ctrl+R: Refresh page
- Ctrl+Shift+R: Hard refresh

### Useful SQL Queries
```sql
-- Count users by organization
SELECT o.name, COUNT(u.id) as user_count 
FROM organizations o 
LEFT JOIN users u ON o.id = u.organization_id 
GROUP BY o.id, o.name;

-- Recent signups
SELECT email, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;

-- Check user roles
SELECT email, role, status 
FROM users 
WHERE organization_id = (
  SELECT organization_id 
  FROM users 
  WHERE email = 'admin@testcompany.com'
);
```

### API Testing with cURL
```bash
# Test signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "firstName": "Test",
    "lastName": "User",
    "organizationName": "Test Org",
    "organizationSize": "small",
    "industry": "Technology",
    "city": "Riyadh"
  }'

# Test signin
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testcompany.com",
    "password": "TestPassword123!"
  }'
```

---

## Contact for Issues

If you encounter any blocking issues:
1. Check the troubleshooting guide above
2. Review Docker logs: `docker-compose logs [service-name]`
3. Check backend logs: `docker-compose logs -f backend`
4. Verify all environment variables are set correctly

Good luck with your testing! 🚀
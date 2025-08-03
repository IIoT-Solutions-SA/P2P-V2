# Story 5: Authentication System Integration

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 8  
**Priority**: High  
**Dependencies**: Story 3 (Backend API), Story 4 (Database Configuration)

## User Story
**As a** developer  
**I want** SuperTokens integrated and configured with both frontend and backend  
**So that** users can securely register, login, and maintain sessions

## Acceptance Criteria
- [ ] SuperTokens core service running in container
- [ ] Frontend SDK integrated with React components
- [ ] Backend SDK integrated with FastAPI middleware
- [ ] Registration flow working end-to-end
- [ ] Login/logout flow working end-to-end
- [ ] Session management configured with proper expiration
- [ ] Password reset flow configured
- [ ] Email verification implemented
- [ ] Protected routes working on both frontend and backend
- [ ] User profile management endpoints created

## Technical Specifications

### 1. SuperTokens Configuration

#### Backend Dependencies
Add to backend/requirements.txt:
```
supertokens-python==0.17.4
```

#### app/core/supertokens.py
```python
from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.emailpassword.interfaces import APIInterface, APIOptions
from supertokens_python.recipe.emailpassword.types import FormField
from supertokens_python.recipe.session.interfaces import SessionContainer
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger

def override_email_password_apis(original_implementation: APIInterface):
    original_sign_up_post = original_implementation.sign_up_post
    original_sign_in_post = original_implementation.sign_in_post
    
    async def sign_up_post(
        form_fields: list[FormField],
        api_options: APIOptions,
        user_context: Dict[str, Any]
    ):
        # Call original implementation
        response = await original_sign_up_post(form_fields, api_options, user_context)
        
        # Add custom logic after user creation
        if hasattr(response, 'user'):
            logger.info(f"New user registered: {response.user.email}")
            # Here you can sync user to your database
            
        return response
    
    async def sign_in_post(
        form_fields: list[FormField],
        api_options: APIOptions,
        user_context: Dict[str, Any]
    ):
        response = await original_sign_in_post(form_fields, api_options, user_context)
        
        if hasattr(response, 'user'):
            logger.info(f"User signed in: {response.user.email}")
            
        return response
    
    original_implementation.sign_up_post = sign_up_post
    original_implementation.sign_in_post = sign_in_post
    return original_implementation

def init_supertokens():
    init(
        app_info=InputAppInfo(
            app_name=settings.PROJECT_NAME,
            api_domain=settings.BACKEND_URL,
            website_domain=settings.FRONTEND_URL,
            api_base_path="/auth",
            website_base_path="/auth"
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.SUPERTOKENS_CONNECTION_URI,
            api_key=settings.SUPERTOKENS_API_KEY,
        ),
        framework='fastapi',
        recipe_list=[
            emailpassword.init(
                override=emailpassword.InputOverrideConfig(
                    apis=override_email_password_apis
                ),
                sign_up_feature=emailpassword.InputSignUpFeature(
                    form_fields=[
                        emailpassword.InputFormField(id="email"),
                        emailpassword.InputFormField(id="password"),
                        emailpassword.InputFormField(id="name", optional=False),
                    ]
                )
            ),
            session.init(
                cookie_domain=settings.COOKIE_DOMAIN if hasattr(settings, 'COOKIE_DOMAIN') else None,
                cookie_same_site="lax",
                session_expired_status_code=401,
                anti_csrf="VIA_TOKEN",
                override=session.InputOverrideConfig(
                    functions=lambda original_implementation: original_implementation
                )
            )
        ],
        mode='asgi'
    )
```

#### Update app/core/config.py
```python
# Add to Settings class:
    # SuperTokens Configuration
    SUPERTOKENS_CONNECTION_URI: str = "http://supertokens:3567"
    SUPERTOKENS_API_KEY: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    COOKIE_DOMAIN: Optional[str] = None
```

### 2. FastAPI Integration

#### Update app/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python import get_all_cors_headers

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.supertokens import init_supertokens
from app.core.database import db_manager
from app.api.v1.api import api_router
from app.api.auth import auth_router

# Initialize SuperTokens
init_supertokens()

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME}")
    await db_manager.init_postgres()
    await db_manager.init_mongodb()
    yield
    # Shutdown
    logger.info("Shutting down")
    await db_manager.close_connections()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Add SuperTokens middleware
app.add_middleware(get_middleware())

# CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type"] + get_all_cors_headers(),
    )

# Include routers
app.include_router(auth_router)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "auth_enabled": True
    }
```

### 3. Authentication Routes

#### app/api/auth.py
```python
from fastapi import APIRouter, Depends, HTTPException
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.emailpassword.asyncio import get_user_by_id
from app.schemas.auth import UserProfile, UpdateUserProfile
from app.services.user_service import UserService
from typing import Optional

auth_router = APIRouter()

@auth_router.get("/user/profile")
async def get_user_profile(session: SessionContainer = Depends(verify_session())):
    """Get current user profile"""
    user_id = session.get_user_id()
    
    # Get user from SuperTokens
    st_user = await get_user_by_id(user_id)
    if not st_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get additional profile data from MongoDB
    profile = await UserService.get_user_profile(user_id)
    
    return UserProfile(
        id=user_id,
        email=st_user.email,
        name=profile.name if profile else "Unknown",
        role=profile.role if profile else "user",
        industry_sector=profile.industry_sector if profile else None,
        location=profile.location if profile else None,
        expertise_tags=profile.expertise_tags if profile else [],
        verified=profile.verified if profile else False,
        language_preference=profile.language_preference if profile else "en"
    )

@auth_router.put("/user/profile")
async def update_user_profile(
    profile_data: UpdateUserProfile,
    session: SessionContainer = Depends(verify_session())
):
    """Update current user profile"""
    user_id = session.get_user_id()
    
    profile = await UserService.update_user_profile(user_id, profile_data.dict(exclude_unset=True))
    
    return {"message": "Profile updated successfully", "profile": profile}

@auth_router.delete("/user/account")
async def delete_user_account(session: SessionContainer = Depends(verify_session())):
    """Delete current user account"""
    user_id = session.get_user_id()
    
    # Delete from SuperTokens and our database
    await UserService.delete_user(user_id)
    await session.revoke_session()
    
    return {"message": "Account deleted successfully"}
```

### 4. Authentication Schemas

#### app/schemas/auth.py
```python
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
    industry_sector: Optional[str] = None
    location: Optional[str] = None
    expertise_tags: List[str] = []
    verified: bool = False
    language_preference: str = "en"

class UpdateUserProfile(BaseModel):
    name: Optional[str] = None
    industry_sector: Optional[str] = None
    location: Optional[str] = None
    expertise_tags: Optional[List[str]] = None
    language_preference: Optional[str] = None

class SessionInfo(BaseModel):
    user_id: str
    session_handle: str
    expires_at: datetime
    
class AuthStatus(BaseModel):
    authenticated: bool
    user: Optional[UserProfile] = None
```

### 5. User Service

#### app/services/user_service.py
```python
from typing import Optional, Dict, Any
from app.models.mongo_models import User
from supertokens_python.recipe.emailpassword.asyncio import delete_user
from app.core.logging import logger

class UserService:
    @staticmethod
    async def get_user_profile(user_id: str) -> Optional[User]:
        """Get user profile from MongoDB"""
        try:
            user = await User.find_one(User.id == user_id)
            return user
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    @staticmethod
    async def create_user_profile(user_id: str, email: str, name: str) -> User:
        """Create user profile in MongoDB"""
        user = User(
            id=user_id,
            email=email,
            name=name,
            role="user",
            verified=False,
            language_preference="en"
        )
        await user.create()
        logger.info(f"User profile created: {email}")
        return user
    
    @staticmethod
    async def update_user_profile(user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user profile"""
        try:
            user = await User.find_one(User.id == user_id)
            if user:
                for key, value in update_data.items():
                    setattr(user, key, value)
                await user.save()
                logger.info(f"User profile updated: {user_id}")
                return user
            return None
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return None
    
    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete user from both SuperTokens and MongoDB"""
        try:
            # Delete from SuperTokens
            await delete_user(user_id)
            
            # Delete from MongoDB
            user = await User.find_one(User.id == user_id)
            if user:
                await user.delete()
            
            logger.info(f"User deleted: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False
```

### 6. Frontend Integration

#### Update frontend/package.json dependencies:
```json
{
  "dependencies": {
    "supertokens-auth-react": "^0.41.0",
    "supertokens-web-js": "^0.8.0"
  }
}
```

#### frontend/src/config/supertokens.ts
```typescript
import SuperTokens from "supertokens-auth-react";
import EmailPassword from "supertokens-auth-react/recipe/emailpassword";
import Session from "supertokens-auth-react/recipe/session";

SuperTokens.init({
    appInfo: {
        appName: import.meta.env.VITE_SUPERTOKENS_APP_NAME || "P2P Sandbox",
        apiDomain: import.meta.env.VITE_SUPERTOKENS_API_DOMAIN || "http://localhost:8000",
        websiteDomain: import.meta.env.VITE_SUPERTOKENS_WEBSITE_DOMAIN || "http://localhost:3000",
        apiBasePath: "/auth",
        websiteBasePath: "/auth"
    },
    recipeList: [
        EmailPassword.init({
            signInAndUpFeature: {
                signUpForm: {
                    formFields: [
                        {
                            id: "email",
                            label: "Email",
                            placeholder: "Your email address"
                        },
                        {
                            id: "password",
                            label: "Password",
                            placeholder: "Password"
                        },
                        {
                            id: "name",
                            label: "Full Name",
                            placeholder: "Your full name"
                        }
                    ]
                }
            }
        }),
        Session.init({
            tokenTransferMethod: "cookie"
        })
    ]
});
```

#### frontend/src/components/Auth/AuthWrapper.tsx
```typescript
import { useEffect, useState } from 'react';
import { SessionAuth } from 'supertokens-auth-react/recipe/session';
import { redirectToAuth } from 'supertokens-auth-react';
import Session from 'supertokens-web-js/recipe/session';

interface AuthWrapperProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

export default function AuthWrapper({ children, requireAuth = false }: AuthWrapperProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    async function checkAuth() {
      try {
        const hasSession = await Session.doesSessionExist();
        setIsAuthenticated(hasSession);
        
        if (requireAuth && !hasSession) {
          redirectToAuth();
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    }

    checkAuth();
  }, [requireAuth]);

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (requireAuth && !isAuthenticated) {
    return null; // Will redirect to auth
  }

  if (requireAuth) {
    return (
      <SessionAuth>
        {children}
      </SessionAuth>
    );
  }

  return <>{children}</>;
}
```

#### frontend/src/components/Auth/UserProfile.tsx
```typescript
import { useState, useEffect } from 'react';
import { useSessionContext } from 'supertokens-auth-react/recipe/session';
import { signOut } from 'supertokens-auth-react/recipe/emailpassword';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import api from '@/lib/api';

interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: string;
  industry_sector?: string;
  location?: string;
  expertise_tags: string[];
  verified: boolean;
  language_preference: string;
}

export default function UserProfileComponent() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const session = useSessionContext();

  useEffect(() => {
    async function fetchProfile() {
      try {
        const response = await api.get('/user/profile');
        setProfile(response.data);
      } catch (error) {
        console.error('Failed to fetch profile:', error);
      } finally {
        setLoading(false);
      }
    }

    if (session.loading === false && session.doesSessionExist) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [session]);

  const handleSignOut = async () => {
    await signOut();
    window.location.href = '/';
  };

  if (loading) {
    return <div>Loading profile...</div>;
  }

  if (!profile) {
    return <div>Profile not found</div>;
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>User Profile</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="font-medium">Name:</label>
          <p>{profile.name}</p>
        </div>
        <div>
          <label className="font-medium">Email:</label>
          <p>{profile.email}</p>
        </div>
        <div>
          <label className="font-medium">Role:</label>
          <p>{profile.role}</p>
        </div>
        <div>
          <label className="font-medium">Verified:</label>
          <p>{profile.verified ? 'Yes' : 'No'}</p>
        </div>
        <Button onClick={handleSignOut} variant="outline" className="w-full">
          Sign Out
        </Button>
      </CardContent>
    </Card>
  );
}
```

#### Update frontend/src/main.tsx
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import SuperTokens, { SuperTokensWrapper } from "supertokens-auth-react"
import App from './App.tsx'
import './config/supertokens.ts'
import './i18n/config.ts'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <SuperTokensWrapper>
      <App />
    </SuperTokensWrapper>
  </React.StrictMode>,
)
```

### 7. Protected Route Component

#### frontend/src/components/ProtectedRoute.tsx
```typescript
import { ReactNode } from 'react';
import AuthWrapper from './Auth/AuthWrapper';

interface ProtectedRouteProps {
  children: ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  return (
    <AuthWrapper requireAuth>
      {children}
    </AuthWrapper>
  );
}
```

### 8. API Client with Auth

#### frontend/src/lib/api.ts
```typescript
import axios from 'axios';
import Session from 'supertokens-web-js/recipe/session';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
});

// Add auth headers automatically
api.interceptors.request.use(async (config) => {
  const hasSession = await Session.doesSessionExist();
  if (hasSession) {
    const userId = await Session.getUserId();
    config.headers['X-User-ID'] = userId;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await Session.attemptRefreshingSession();
      // Retry the request
      return api.request(error.config);
    }
    return Promise.reject(error);
  }
);

export default api;
```

## Implementation Steps

1. **Install SuperTokens Dependencies**
   ```bash
   # Backend
   cd backend
   pip install supertokens-python
   
   # Frontend
   cd frontend
   npm install supertokens-auth-react supertokens-web-js
   ```

2. **Configure SuperTokens**
   - Create SuperTokens configuration files
   - Update environment variables
   - Initialize SuperTokens in both frontend and backend

3. **Create Authentication Components**
   - User profile components
   - Protected route wrapper
   - Auth status indicators

4. **Test Authentication Flow**
   - Registration works end-to-end
   - Login/logout functionality
   - Session persistence
   - Protected routes redirect properly

## Testing Checklist
- [ ] User can register with email and password
- [ ] User can login and logout
- [ ] Sessions persist across browser refresh
- [ ] Protected routes redirect to login
- [ ] User profile displays correctly
- [ ] Password reset flow works
- [ ] Email verification works (if configured)
- [ ] API calls include authentication headers

## Docker Configuration (for Story 6)
```yaml
# SuperTokens service
supertokens:
  image: registry.supertokens.io/supertokens/supertokens-postgresql:7.0
  environment:
    POSTGRESQL_CONNECTION_URI: postgresql://p2p_user:changeme@postgres:5432/supertokens
  ports:
    - "3567:3567"
  depends_on:
    - postgres
```

## Dependencies
- Story 3 (Backend API setup)
- Story 4 (Database configuration)

## Notes
- Store sensitive configuration in environment variables
- Use secure cookie settings in production
- Implement proper CORS configuration
- Consider implementing refresh token rotation
- Plan for social login integration in future stories
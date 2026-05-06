# P2P-V2 Project — Complete Deep-Dive Explanation

## 1. What Is This Project?

**P2P (Peer-to-Peer) Manufacturing Knowledge Platform** — a web app where manufacturing professionals in Saudi Arabia can:
- **Share Use Cases**: Publish detailed "success stories" about how they solved factory problems (e.g., "How we reduced downtime by 30% with IoT sensors").
- **Ask Questions in a Forum**: A Stack Overflow-style Q&A for manufacturing engineers.
- **Manage Organizations**: Each company is an "organization." The first person to sign up from a company domain becomes the Admin and can invite team members.

---

## 2. What Is SuperTokens & Why Is It Used?

**SuperTokens** is an **open-source authentication service** (like Auth0 or Firebase Auth, but self-hosted). It runs as a **separate Docker container** (on port `3567`) and handles all the complex, security-critical parts of authentication.

### What SuperTokens does in this project:
| Responsibility | How it works |
|---|---|
| **Stores passwords securely** | It hashes passwords using bcrypt. The backend code **never** touches raw passwords — it delegates to SuperTokens. |
| **Manages sessions** | Instead of JWTs stored in `localStorage` (which are vulnerable to XSS attacks), SuperTokens creates **httpOnly cookies**. These cookies are automatically attached to every HTTP request by the browser and **cannot be read by JavaScript**, making them far more secure. |
| **Email verification tokens** | When an admin signs up, SuperTokens generates a unique, time-limited token. The backend sends an email containing a link with this token. When clicked, SuperTokens validates it. |
| **Password reset tokens** | Same mechanism — generates a secure token, which is sent via email and validated when the user submits a new password. |

### Where SuperTokens is configured:

**Backend** — [supertokens.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/core/supertokens.py):
```python
# Initializes 3 "recipes" (SuperTokens modules):
recipe_list=[
    emailpassword.init(...)     # 1. Email/Password login
    emailverification.init(...) # 2. Email verification (mode="REQUIRED")
    session.init(...)           # 3. Session management (httpOnly cookies)
]
```
The `cookie_same_site="lax"` and `cookie_secure` settings ensure cookies work correctly in both development (HTTP) and production (HTTPS).

**Frontend** — [supertokens.ts](file:///c:/iiot/p2p/P2P-V2/p2p-frontend-app/src/config/supertokens.ts):
```typescript
// Tells the SuperTokens frontend SDK where the backend lives
SuperTokens.init({
    appInfo: {
        apiDomain: API_BASE_URL,       // e.g., http://localhost:8000
        websiteDomain: WEBSITE_BASE_URL, // e.g., http://localhost:5173
        apiBasePath: "/api/v1/auth",     // All auth routes under this path
    },
    recipeList: [EmailPassword.init(), EmailVerification.init(), Session.init()]
});
```

**Docker** — SuperTokens runs as its own container and stores its data in PostgreSQL:
```yaml
supertokens:
    image: registry.supertokens.io/supertokens/supertokens-postgresql:11.0
    environment:
      - POSTGRESQL_CONNECTION_URI=postgresql://p2p_user:iiot123@postgres:5432/supertokens
```

---

## 3. How Authentication & Authorization Works (Step by Step)

### 3A. Admin Signup Flow

```
User fills signup form → Frontend POSTs to /api/v1/auth/custom-signup
```

The backend ([supertokens_auth.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py)) then does this:

1. **Check if user already exists** — queries both PostgreSQL and MongoDB by email
2. **Check for invite token** — if `inviteToken` is present → this is a member signup; if absent → this is an admin signup
3. **Call SuperTokens** — `sign_up("public", email, password)` → SuperTokens hashes the password and stores the user, returning a `supertokens_id`
4. **Create user in BOTH databases** — calls `UserService.create_user_with_profile()` which:
   - Creates a row in **PostgreSQL** `users` table (stores `supertokens_id`, `email`, `name`, `role`)
   - Extracts the email domain (e.g., `acme.com` from `john@acme.com`)
   - Checks if an Organization with that domain exists in MongoDB:
     - **No** → Creates a new Organization document
     - **Yes** → Checks if an admin already exists (enforces **single admin per org** rule)
   - Creates a user document in **MongoDB** (stores extended profile: `title`, `expertise_tags`, `organization_id`, etc.)
5. **Send verification email** — SuperTokens generates a token, the backend overrides the default email sender with a custom branded HTML email
6. **Return** — `{ requiresEmailVerification: true }` → Frontend redirects to "Check your email" page

### 3B. Invited Member Signup Flow

1. Admin clicks "Send Invitation" → backend generates a `secrets.token_urlsafe(32)` token → stores an `Invitation` document in MongoDB → sends email with link: `{website}/join?token={token}&email={email}`
2. Invited user clicks link → Frontend loads the `MemberSignup` page → validates the token via API
3. On submit, the same `/custom-signup` endpoint is called, but with `inviteToken` in the body
4. Backend validates the token (checks it's not expired or used), finds the inviter's organization
5. Creates user in SuperTokens + both databases, linking them to the **inviter's organization**
6. **Auto-verifies email** — since they received an invitation email, there's no need for verification. The backend creates a verification token and immediately consumes it:
   ```python
   token_result = await create_email_verification_token("public", recipe_user_id, email)
   await verify_email_using_token("public", token_result.token)
   ```
7. Marks the invitation as `used = True`

### 3C. Login Flow

1. Frontend POSTs `{ email, password }` to `/api/v1/auth/custom-signin`
2. Backend calls `sign_in("public", email, password)` — SuperTokens verifies credentials
3. **Checks email verification** — `is_email_verified(recipe_user_id)` → if not verified, returns `403 EMAIL_NOT_VERIFIED`
4. **Creates a session** — `create_new_session(request, response, recipe_user_id)` → SuperTokens sets `httpOnly` cookies on the response
5. Frontend receives cookies → on next page load, `Session.doesSessionExist()` returns `true` → fetches profile from `/api/v1/auth/me`

### 3D. How Authorization (Protection) Works

Every protected API endpoint uses FastAPI's dependency injection:
```python
@router.get("/posts")
async def get_posts(session: SessionContainer = Depends(verify_session())):
    user_id = session.get_user_id()  # Extracts supertokens_id from the cookie
```
- If the request has no valid session cookie → SuperTokens middleware returns `401 Unauthorized`
- If valid → the `supertokens_id` is extracted from the session, then used to look up the user in PostgreSQL and MongoDB

**Role-based authorization** (e.g., only admins can send invitations) is checked manually:
```python
if mongo_user.role != "admin":
    return JSONResponse(status_code=403, content={"message": "Admin only"})
```

---

## 4. How the Dual-Database System Works & Why

### Why Two Databases?

| Database | What it stores | Why |
|---|---|---|
| **PostgreSQL** | Core user credentials (`supertokens_id`, `email`, `role`), sessions, uploaded file metadata (`UserMedia`) | ACID transactions ensure data integrity for auth-critical data. SuperTokens *requires* PostgreSQL. |
| **MongoDB** | Rich profiles, organizations, forum posts (with nested replies, attachments, tags), use cases (50+ fields with nested objects) | Flexible schemas — a UseCase document has deeply nested objects like `business_challenge.specificProblems[]`, `results.quantitativeResults[]`. This would require 10+ tables in PostgreSQL but is a single document in MongoDB. |

### The User Linking Chain

When a request comes in, the system resolves the user identity through this chain:

```
Browser cookie → SuperTokens session → supertokens_id
    → PostgreSQL users table (lookup by supertokens_id) → email
    → MongoDB users collection (lookup by email) → MongoDB ObjectId (_id)
```

This `_id` (ObjectId) is what's stored as `author_id` in forum posts, `submitted_by` in use cases, etc.

### Database Models

**PostgreSQL Tables** ([pg_models.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/models/pg_models.py)):
- `users` — Core auth data + S3 profile picture URL
- `user_sessions` — Session tracking for analytics
- `user_media` — Tracks every file uploaded to S3 (for auditing and cascade deletion)
- `system_configs` — Key-value app settings

**MongoDB Collections** ([mongo_models.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/models/mongo_models.py)):
- `users` — Extended profiles (expertise tags, title, company, organization link)
- `organizations` — Company data with domain-based uniqueness
- `forum_posts` — Posts with `liked_by[]` array, `attachments[]`, view counts
- `forum_replies` — Threaded replies via `parent_reply_id`
- `use_cases` — 50+ fields (basic info, business challenge, solution, implementation, results, media)
- `use_case_drafts` — Mirrors UseCase but all fields are `Optional` for partial saves
- `user_activities` — Activity log (question, answer, like, bookmark, view)
- `user_stats` — Aggregated stats (reputation score, activity level)
- `user_bookmarks` — Saved posts/use cases
- `invitations` — Invite tokens with expiry

---

## 5. How the Project Sends Emails

### Email Infrastructure

The project uses **Gmail SMTP** via the `fastapi-mail` library. Configuration is in [config.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/core/config.py):
```python
MAIL_USERNAME: str = "coding@iiotsolutions.sa"
MAIL_PASSWORD: str = ""  # Gmail App Password - set in .env
MAIL_SERVER: str = "smtp.gmail.com"
MAIL_PORT: int = 587     # TLS port
```

### Three Email Services

| Service File | Sends | Triggered By |
|---|---|---|
| [email_verification_service.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/services/email_verification_service.py) | "Verify your email" link | Admin signup |
| [password_reset_service.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/services/password_reset_service.py) | "Reset your password" link | Forgot password request |
| [email_service.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/services/email_service.py) | Invitation emails + Welcome emails | Admin invites a member |

### How SuperTokens Delegates to Custom Email Senders

SuperTokens has its own default email sender, but this project **overrides** it to send branded HTML emails. This is done in [supertokens.py](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/core/supertokens.py):

```python
def custom_email_delivery_override(original_implementation):
    async def send_email(template_vars, user_context):
        # Instead of SuperTokens' default email, call OUR custom service
        await send_email_verification(
            email=template_vars.user.email,
            email_verify_url=template_vars.email_verify_link
        )
    original_implementation.send_email = send_email
    return original_implementation
```

Each email service sends **beautifully styled HTML emails** with gradient headers, call-to-action buttons, and fallback text links.

### Development Convenience

In development, the verification/reset URLs are also printed to the **terminal** so developers don't need to check a real inbox:
```
================================================================================
📧 EMAIL VERIFICATION SENT TO: john@acme.com
🔗 Localhost verification link (for dev testing):
   http://localhost:5173/auth/verify-email?token=abc123&tenantId=public
================================================================================
```

---

## 6. How File Storage (S3) Works

### Storage Architecture

The project uses **OCI Object Storage** (Oracle Cloud, S3-compatible API) via the `boto3` library. The [S3Service](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/services/s3_service.py) manages three buckets:

| Bucket | Purpose | Max File Size | Allowed Types |
|---|---|---|---|
| `p2p-profile-images` | Profile pictures | 5 MB | JPEG, PNG, WebP |
| `p2p-forum-media` | Forum post attachments | 50 MB | Images + MP4/WebM videos |
| `p2p-usecase-media` | Use case images/videos | 50 MB | Images + MP4/WebM videos |

### Upload Flow

1. Frontend sends file as `FormData` to `/api/v1/media/profile-picture`
2. Backend validates file type and size
3. Generates a unique S3 key: `profile-pictures/{user_id}/{uuid}.jpg`
4. Uploads to S3 via `put_object()`
5. Generates a public URL
6. Creates a `UserMedia` record in PostgreSQL (for tracking/auditing)
7. Returns the URL to the frontend, which stores it in the user profile or post

### Cascade Deletion

When a user account is deleted, the system:
1. Queries PostgreSQL `UserMedia` for all files belonging to that user
2. Deletes each file from S3 via `delete_object()`
3. Deletes the PostgreSQL records (cascade via foreign key)

---

## 7. How the Frontend Works

### Environment Detection ([environment.ts](file:///c:/iiot/p2p/P2P-V2/p2p-frontend-app/src/config/environment.ts))

The frontend auto-detects where it's running:
```typescript
const isProductionServer = window.location.hostname === 'peerlink.c4ir.sa';
export const API_BASE_URL = isProductionServer
    ? 'https://peerlink.c4ir.sa'
    : 'http://localhost:8000';
```

### Auth State Management ([AuthContext.tsx](file:///c:/iiot/p2p/P2P-V2/p2p-frontend-app/src/contexts/AuthContext.tsx))

The entire app is wrapped in an `AuthProvider` that:
1. **On app load**: Checks `Session.doesSessionExist()` (SuperTokens SDK checks for valid cookies)
2. **If session exists**: Fetches the full user profile from `/api/v1/auth/me` (which returns user + organization data)
3. **Stores globally**: `{ user, organization, isAuthenticated }` — accessible from any component via `useAuth()` hook
4. **All API calls** use `credentials: 'include'` to automatically send session cookies

### Routing

Protected routes are wrapped in a `ProtectedRoute` component that redirects to `/login` if `isAuthenticated` is `false`.

---

## 8. How Docker Orchestrates Everything

The [docker-compose.yml](file:///c:/iiot/p2p/P2P-V2/docker/docker-compose.yml) defines **5 services** that start in a specific order:

```
1. postgres (port 5432) + mongodb (port 27017)  ← Start first
           ↓ (healthcheck passes)
2. supertokens (port 3567)                       ← Waits for postgres
           ↓ (service_started)
3. backend (port 8000)                            ← Waits for all 3 above
   → Runs Alembic migrations
   → Starts uvicorn
           ↓ (healthcheck passes on /api/v1/health)
4. frontend (port 5173)                           ← Waits for backend
```

The backend container has a **wait script** that polls PostgreSQL and MongoDB sockets before running migrations:
```bash
while ! python -c 'import socket; s.connect(("postgres", 5432))'; do sleep 1; done
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 9. The Reputation & Gamification System

The [UserActivityService](file:///c:/iiot/p2p/P2P-V2/p2p-backend-app/app/services/user_activity_service.py) tracks everything users do and calculates a reputation score:

### Points System
| Action | Points |
|---|---|
| Ask a question (forum post) | +2 |
| Answer a question (reply) | +3 |
| Best answer selected | +15 |
| Submit a use case | +10 |
| Receive an upvote | +1 |

### Activity Level
Based on a **30-day rolling window**: `min(100%, (activities_in_30_days / 20) × 100%)`

This is recalculated every time a user performs an action (via `recalculate_user_stats()`).

---

## 10. Key Design Patterns Used

| Pattern | Where | Why |
|---|---|---|
| **Service Layer** | `app/services/` (9 files) | Separates business logic from API route handlers |
| **Repository Pattern** | SQLAlchemy sessions + Beanie ODM | Abstracts database operations |
| **Dependency Injection** | FastAPI `Depends(get_db)`, `Depends(verify_session)` | Clean, testable code |
| **Singleton** | `DatabaseManager`, `S3Service` | One connection pool shared across requests |
| **Soft Deletes** | Forum posts/use cases set `status = "deleted"` | Audit trail, data recovery |
| **Slug-based URLs** | `/usecases/acme-corp/predictive-maintenance` | SEO-friendly |
| **Atomic Dual-DB Writes** | `UserService.create_user_with_profile()` | If MongoDB insert fails, PostgreSQL is rolled back |

---

## 11. Summary — How Everything Connects

```
┌─ Browser (React + Vite) ─────────────────────────────────────┐
│  SuperTokens SDK manages session cookies automatically       │
│  AuthContext.tsx holds global user state                      │
│  All API calls use fetch() with credentials: 'include'       │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTP + Cookies
                   ▼
┌─ FastAPI Backend ────────────────────────────────────────────┐
│  SuperTokens Middleware → verifies session cookies            │
│  CORS Middleware → allows frontend origin                     │
│  API Routes → auth, forum, usecases, media, dashboard        │
│  Services → UserService, ForumService, S3Service, etc.       │
└────┬──────────┬──────────┬───────────────────────────────────┘
     │          │          │
     ▼          ▼          ▼
 PostgreSQL   MongoDB   SuperTokens Core
 (users,      (profiles, (password hashing,
  media        forums,    sessions,
  tracking)    usecases)  email tokens)
                          │
                          ▼
                     Gmail SMTP
                   (sends branded
                    HTML emails)
```

# Backend Application Exploration Log

**Date:** 2026-03-05
**Session:** 002
**Agent:** Backend Explorer

## Objective

Comprehensive exploration of the `p2p-backend-app/` directory — every file, every endpoint, every model, every service, all architectural patterns and dependencies.

## Summary

The backend is a production-grade FastAPI application with ~2,433 lines of service code, dual-database architecture (PostgreSQL + MongoDB), SuperTokens authentication, AWS S3 file management, and a complete service layer pattern. It serves 8 API endpoint groups with comprehensive user management, forums, use cases, invitations, media uploads, and dashboard analytics.

---

## Directory Structure

```
p2p-backend-app/
├── app/
│   ├── main.py                         (74 lines) - FastAPI app init & lifespan
│   ├── __init__.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── api.py                  (26 lines) - Router aggregation
│   │   │   └── endpoints/
│   │   │       ├── supertokens_auth.py (250+ lines) - Custom signup & auth
│   │   │       ├── auth.py            (387 lines) - User profile & session mgmt
│   │   │       ├── forum.py           (250+ lines) - Forum CRUD & interactions
│   │   │       ├── usecases.py        (250+ lines) - Use case management
│   │   │       ├── invites.py         (259 lines) - Invitation system
│   │   │       ├── media.py           (484 lines) - File uploads (S3)
│   │   │       ├── dashboard.py       (100+ lines) - Stats & activities
│   │   │       ├── health.py          - Health check
│   │   │       └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── main.py                    (106 lines) - FastAPI app setup & lifespan
│   │   ├── config.py                  (69 lines) - Settings & env config
│   │   ├── database.py                (106 lines) - Database manager (dual DBs)
│   │   ├── supertokens.py             (110 lines) - SuperTokens init & overrides
│   │   ├── logging.py                 (53 lines) - Loguru configuration
│   │   └── __init__.py
│   ├── models/
│   │   ├── pg_models.py               (63 lines) - SQLAlchemy models
│   │   ├── mongo_models.py            (318 lines) - Beanie document models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── usecase.py                 (100+ lines) - Use case Pydantic schemas
│   │   ├── forum.py                   - Forum schemas
│   │   ├── invitation.py              - Invitation req/res models
│   │   ├── common.py                  - Shared schemas
│   │   └── __init__.py
│   └── services/                      (2,433 total lines)
│       ├── database_service.py        (200+ lines) - UserService
│       ├── invitation_service.py      (196 lines) - Invitation management
│       ├── email_service.py           (300+ lines) - Invitation & welcome emails
│       ├── email_verification_service.py (176 lines) - Email verification
│       ├── password_reset_service.py  (175 lines) - Password reset emails
│       ├── s3_service.py              (150+ lines) - AWS S3 file uploads
│       ├── forum_service.py           - Forum operations
│       ├── usecase_service.py         (100+ lines) - Use case submission
│       ├── user_activity_service.py   (327 lines) - Activity tracking & stats
│       └── __init__.py
├── alembic/
│   ├── alembic.ini                    (45 lines) - Migration config
│   ├── env.py                         - Alembic environment setup
│   └── versions/
│       ├── 5154fc59743b_initial_migration.py        (66 lines)
│       ├── 8f5515e822b8_add_supertokens_id.py
│       └── abc123def456_add_media_support.py
├── scripts/
│   ├── seed_all.py                    (80+ lines) - Master seeding orchestrator
│   ├── seed_db_users.py               - 18 demo users
│   ├── seed_team_members.py           - 6 IIoT Solutions team members
│   ├── seed_usecases.py               - Use cases
│   ├── seed_forums.py                 - Forum posts
│   ├── seed_user_activities.py        - Activity logs
│   ├── verify_existing_users.py       - Bulk email verification
│   ├── migrate_usecase_fields.py      - Field migration utility
│   ├── remove_usecases.py             - Cleanup script
│   └── usecases/                      - Individual team member seeders
├── requirements.txt                   (42 dependencies)
└── logs/                              - Application log directory
```

---

## Core Application Files

### `app/main.py` (74 lines)
**Purpose**: FastAPI app initialization and startup/shutdown lifecycle

- FastAPI app with lifespan context manager
- SuperTokens middleware added FIRST (handles auth endpoints)
- CORS middleware with dynamic origin configuration from SuperTokens
- Database initialization on startup (PostgreSQL + MongoDB with retry logic)
- API router inclusion at `/api/v1` prefix

**Startup Flow**:
1. Initialize SuperTokens
2. Connect to PostgreSQL (with retry logic)
3. Connect to MongoDB (with retry logic)
4. Setup CORS headers from SuperTokens config

---

### `app/core/config.py` (69 lines)
**Class**: `Settings(BaseSettings)`

| Setting | Default | Purpose |
|---------|---------|---------|
| `DATABASE_URL` | (env) | PostgreSQL async connection string |
| `MONGODB_URL` | (env) | MongoDB connection string |
| `SUPERTOKENS_CONNECTION_URI` | (env) | SuperTokens core URI |
| `API_DOMAIN` | `http://localhost:8000` | Backend URL |
| `WEBSITE_DOMAIN` | `http://localhost:5173` | Frontend URL |
| `COOKIE_DOMAIN` | Optional | Cookie scope |
| `S3_PROFILE_PICTURES_BUCKET` | `p2p-prod-profile-images` | Profile pics bucket |
| `S3_FORUM_MEDIA_BUCKET` | `p2p-prod-forum-media` | Forum media bucket |
| `S3_USECASE_MEDIA_BUCKET` | `p2p-prod-usecase-media` | Use case media bucket |
| `BACKEND_CORS_ORIGINS` | localhost variants | CORS allowed origins |

---

### `app/core/database.py` (106 lines)
**Class**: `DatabaseManager` (singleton pattern)

| Method | Description |
|--------|-------------|
| `init_postgres()` | Async engine with pool (size: 20, overflow: 40, recycle: 3600s). Creates tables. |
| `init_mongodb()` | Motor async client with Beanie ODM. Pool: 20 max, 5 min. DB: `p2p_sandbox`. |
| `close_connections()` | Cleanup on shutdown |
| `get_db()` | AsyncGenerator yielding SQLAlchemy sessions (dependency injection) |

---

### `app/core/supertokens.py` (110 lines)

| Function | Description |
|----------|-------------|
| `custom_email_delivery_override()` | Intercepts verification emails → uses custom `EmailVerificationService` |
| `custom_password_reset_email_override()` | Intercepts reset emails → uses custom `PasswordResetService` |
| `init_supertokens()` | EmailPassword recipe with custom form fields, REQUIRED email verification, session config |

**Custom Form Fields**: email, password, firstName, lastName, companyName, industrySector, companySize, city

---

## Database Models

### PostgreSQL Models (`pg_models.py`)

**User Table**:
- `id`: UUID (PK)
- `supertokens_id`: String(255) — link to SuperTokens
- `email`: String(255) — unique, indexed
- `name`: String(255)
- `role`: String(50) — default "user"
- `is_active`, `is_verified`: Boolean
- `profile_picture_url`: String(500) — S3 URL
- `created_at`, `updated_at`: DateTime with timezone

**UserSession Table**:
- `id`: UUID (PK)
- `user_id`: UUID (FK → User, CASCADE)
- `session_token`: String(255) — unique, indexed
- `expires_at`: DateTime
- `ip_address`: String(45), `user_agent`: Text

**UserMedia Table**:
- `id`: UUID (PK)
- `user_id`: UUID (FK → User)
- `file_type`: String(50) — profile_picture | forum_attachment | usecase_media
- `original_filename`, `s3_key`, `s3_url`: String
- `file_size`: Integer, `mime_type`: String(100)
- `context_id`: String(255) — post_id, usecase_id, etc.

**SystemConfig Table**:
- `id`: Integer (PK)
- `key`: String(255) — unique
- `value`: Text, `description`: Text

---

### MongoDB Models (`mongo_models.py`, 318 lines)

**User Document**:
- `email` (EmailStr, indexed), `name`, `organization_id`, `industry_sector`, `location`, `company`, `title`
- `expertise_tags`: List[str], `verified`: bool, `role`: str
- `language_preference`: "en", `profile_picture_url`: Optional S3 URL

**Organization Document**:
- `name`, `domain` (indexed), `industry_sector`, `size`, `country`, `city`
- `is_active`: bool

**ForumPost Document**:
- `author_id`, `title`, `content`, `category` (indexed), `tags` (indexed)
- `attachments`: List[Dict] — [{url, filename, type, size}]
- `best_answer_id`, `status`: "open"
- `view_count`, `reply_count`, `upvotes`: int
- `liked_by`: List[str], `is_pinned`, `has_best_answer`: bool

**ForumReply Document**:
- `post_id` (indexed), `author_id` (indexed), `content`
- `parent_reply_id` (indexed) — enables nested replies
- `attachments`, `upvotes`, `liked_by`, `is_best_answer`

**UseCase Document** (~230 fields total):
- **Core**: submitted_by, title, problem_statement, solution_description, vendor_info, cost_estimate, impact_metrics, industry_tags, region, location {lat, lng}
- **Rich Content**: executive_summary, business_challenge, solution_details, implementation_details, challenges_and_solutions, results, technical_architecture, future_roadmap, lessons_learned
- **Media**: images (List[str] S3 URLs), videos (List[Dict])
- **Metadata**: title_slug, company_slug (indexed), status, views, downloads
- **Interaction**: view_count, like_count, bookmark_count, liked_by

**UseCaseDraft Document**: Mirrors UseCase with all Optional fields, supports multi-step wizard (current_step: 1-7)

**UserActivity Document**: user_id, activity_type, target_id, target_title, target_category, description

**UserStats Document**: questions_asked, answers_given, best_answers, use_cases_submitted, bookmarks_saved, total_upvotes_received, reputation_score, activity_level, connections_count, draft_posts

**UserBookmark Document**: user_id, target_type, target_id, target_title, target_category

**DraftPost Document**: user_id, title, content, post_type, category, tags

**Invitation Document**: email (indexed), token (unique indexed), invited_by_id/email/name, expires_at (indexed), used, used_at

---

## API Endpoints

### Router Aggregation (`api/v1/api.py`)
```
/api/v1/auth       → supertokens_auth.router + auth.router
/api/v1/health     → health.router
/api/v1/dashboard  → dashboard.router
/api/v1/forum      → forum.router
/api/v1/use-cases  → usecases.router
/api/v1/invites    → invites.router
/api/v1/media      → media.router
```

### Custom Signup (`supertokens_auth.py`, 250+ lines)

**POST `/api/v1/auth/custom-signup`**
- Request: `{email, password, firstName, lastName, companyName, industrySector, companySize, city, inviteToken?, role?}`
- Flow:
  1. Check existing user in PostgreSQL & MongoDB
  2. Validate invite token if provided
  3. Determine role (admin/member) based on invite or explicit param
  4. Call SuperTokens `sign_up()`
  5. Create user in both databases via `UserService.create_user_with_profile()`
  6. For invited members: auto-verify email, mark invitation used
  7. For admins: send verification email
- Response: `{status: "OK"|"ERROR", message, requiresEmailVerification}`

### User Profile (`auth.py`, 387 lines)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/auth/me` | Current user profile + organization (session required) |
| PUT | `/api/v1/auth/profile` | Update name, title, location, expertise tags |
| PUT | `/api/v1/auth/email` | Change email (requires password verification) |
| PUT | `/api/v1/auth/password` | Change password (requires current password) |
| GET | `/api/v1/auth/users/organization` | List all organization members |

### Forum (`forum.py`, 250+ lines)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/forum/posts` | Create forum post, log activity |
| GET | `/forum/posts` | List posts (category filter, pagination, sorted by -created_at) |
| GET | `/forum/posts/{id}` | Full post with nested comments |
| POST | `/forum/posts/{id}/like` | Toggle like (one per user) |
| POST | `/forum/posts/{id}/replies` | Create reply with nesting support |
| POST | `/forum/replies/{id}/like` | Like a reply |
| GET/POST | `/forum/bookmarks` | Save/unsave posts |
| GET | `/forum/categories` | Dynamic categories with counts |

### Use Cases (`usecases.py`, 250+ lines)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/use-cases/` | List with category, search, sort, pagination |
| GET | `/use-cases/categories` | Categories with counts |
| GET | `/use-cases/stats` | Platform statistics |
| GET | `/use-cases/contributors` | Top companies by contribution |
| GET | `/use-cases/by-id/{id}` | Full use case for editing |
| GET | `/use-cases/{company}/{title}` | Detailed view by slugs |
| POST | `/use-cases/` | Submit new use case |
| PUT | `/use-cases/{id}` | Edit use case |
| PATCH | `/use-cases/{id}/publish` | Publish draft |
| POST | `/use-cases/{id}/like` | Like/unlike |
| POST | `/use-cases/{id}/bookmark` | Bookmark |
| DELETE | `/use-cases/{id}` | Delete use case |

### Media (`media.py`, 484 lines)

| Method | Endpoint | Limits |
|--------|----------|--------|
| POST | `/media/profile-picture` | JPEG/PNG/WebP, 5MB max |
| POST | `/media/forum-attachment` | Images 5MB / Videos 50MB |
| POST | `/media/usecase-media` | Up to 10 files |
| DELETE | `/media/{media_id}` | Owner only |
| GET | `/media/user/{user_id}` | Owner/admin only |

### Invitations (`invites.py`, 259 lines)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/invites/send` | Admin sends email invitation |
| GET | `/invites/validate/{token}` | Validate token (not expired, not used) |
| GET | `/invites/all` | All invitations (admin: all, user: own) |
| GET | `/invites/pending` | User's pending invitations |
| POST | `/invites/mark-used/{token}` | Mark invitation used |
| DELETE | `/invites/{id}` | Cancel invitation (sender/admin) |

### Dashboard (`dashboard.py`, 100+ lines)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/stats` | User stats (9 metrics) |
| GET | `/dashboard/activities` | Community activity feed |
| GET | `/dashboard/bookmarks` | User's bookmarks |
| POST | `/dashboard/drafts` | Create draft |
| GET | `/dashboard/drafts` | Get user's drafts |

---

## Service Layer

### UserService (`database_service.py`, 200+ lines)

| Method | Description |
|--------|-------------|
| `create_user_with_profile(db, supertokens_id, email, profile_data)` | PRIMARY: Creates user in PG + MongoDB, handles organization |
| `get_user_by_email_pg(db, email)` | Lookup by email |
| `get_user_by_supertokens_id(db, id)` | Lookup by SuperTokens ID |
| `get_user_by_id_pg(db, id)` | Lookup by UUID |
| `update_user_pg(db, id, name, email)` | Update PG record |
| `delete_user_pg(db, id)` | Delete from PG |
| `create_user_mongo(email, name, **kwargs)` | Create MongoDB profile |
| `get_user_by_email_mongo(email)` | Lookup MongoDB profile |

### InvitationService (`invitation_service.py`, 196 lines)

| Method | Description |
|--------|-------------|
| `generate_invite_token()` | URL-safe random token |
| `create_invitation(email, invited_by, website_url)` | 7-day expiry, sends email, hardcoded prod URL |
| `validate_invitation(token)` | Check exists, not used, not expired |
| `mark_invitation_used(token)` | Sets used=True |
| `get_pending_invitations(invited_by_id)` | Active invitations |
| `cancel_invitation(invitation_id, user_id)` | Sender/admin only |

### Email Services

**EmailService** (`email_service.py`, 300+ lines):
- Gmail SMTP (`p2p_c4ir@iiotsolutions.sa`)
- `send_invitation_email()`, `send_welcome_email()`
- TEST_MODE redirects to test address

**EmailVerificationService** (`email_verification_service.py`, 176 lines):
- `send_email_verification(email, url)` → production URL: `15.185.167.236:5173/auth/verify-email`

**PasswordResetService** (`password_reset_service.py`, 175 lines):
- `send_password_reset_email(email, url)` → production URL: `15.185.167.236:5173/reset-password`

### S3Service (`s3_service.py`, 150+ lines)

| Method | Bucket | Key Pattern |
|--------|--------|-------------|
| `upload_profile_picture()` | p2p-prod-profile-images | `profile-pictures/{user_id}/{uuid}.{ext}` |
| `upload_forum_attachment()` | p2p-prod-forum-media | `forum-attachments/{post_id}/{uuid}.{ext}` |
| `upload_usecase_media()` | p2p-prod-usecase-media | `use-cases/{usecase_id}/{uuid}.{ext}` |
| `delete_file()` | varies | Deletes from S3 |

AWS Region: `me-south-1` (Middle East)

### UserActivityService (`user_activity_service.py`, 327 lines)

| Method | Description |
|--------|-------------|
| `log_activity(user_id, type, target_id, ...)` | Records activity, triggers stats recalc |
| `get_user_activities(user_id, limit)` | User's recent activities |
| `get_community_activities(limit)` | Community-wide feed |
| `recalculate_user_stats(user_id)` | Weighted reputation scoring |
| `add_bookmark(user_id, type, id, title)` | Bookmark item |
| `get_user_bookmarks(user_id, limit)` | User's bookmarks |
| `create_draft_post(...)` | Save draft |
| `get_user_drafts(user_id)` | User's drafts |

**Reputation Scoring**:
- 2 pts/question, 3 pts/answer, 15 pts/best answer
- 10 pts/use case, 1 pt/upvote
- Activity level: 30-day window, capped at 100%

### UseCaseSubmissionService (`usecase_service.py`, 100+ lines)

- `create_use_case(db, user_supertokens_id, data)` → Resolves user PG→MongoDB, gets/creates org, generates URL slugs, maps form data to rich UseCase document

---

## Dependencies (`requirements.txt`, 42 packages)

**FastAPI & Server**: fastapi==0.109.0, uvicorn[standard]==0.27.0

**Database**: sqlalchemy==2.0.25, asyncpg==0.29.0, alembic==1.13.1, motor==3.3.2, beanie==1.24.0, pymongo==4.6.0

**Authentication**: supertokens-python==0.30.0, passlib[bcrypt]==1.7.4, python-jose[cryptography]==3.3.0

**Email**: fastapi-mail==1.4.1

**AWS**: boto3==1.34.0, botocore==1.34.0

**Utilities**: pydantic==2.10.6, pydantic-settings==2.1.0, python-dotenv==1.0.0, email-validator==2.1.0, tenacity==8.2.3, httpx==0.26.0, python-multipart==0.0.6, loguru==0.7.2

---

## Database Migrations (Alembic)

| Migration | Description |
|-----------|-------------|
| `5154fc59743b` | Initial: creates users, user_sessions, system_configs tables with indexes |
| `8f5515e822b8` | Adds supertokens_id column to users |
| `abc123def456` | Adds user_media table + profile_picture_url to users |

Config: `postgresql+asyncpg://p2p_user:iiot123@localhost:5432/p2p_sandbox`
Post-write hook: black formatter

---

## Seeding Scripts

| Script | Purpose |
|--------|---------|
| `seed_all.py` | Master orchestrator (13-step process) |
| `seed_db_users.py` | 18 demo users |
| `seed_team_members.py` | 6 IIoT Solutions team (Aadil admin + 5 members) |
| `seed_usecases.py` | Use case documents |
| `seed_forums.py` | Forum posts and replies |
| `seed_user_activities.py` | Activity logs |
| `verify_existing_users.py` | Bulk email verification |
| `migrate_usecase_fields.py` | Data migration utility |
| `remove_usecases.py` | Cleanup script |
| `usecases/seed_*.py` | Individual team member use case seeders |

**Organization seeding strategy**: Create Aadil as admin first → retrieve org_id → assign to other 5 members

---

## Critical Flows

### User Signup (Admin)
```
POST /custom-signup → Create SuperTokens user → Create PG User →
Create/find Organization by domain → Create MongoDB profile with org_id →
Send verification email → Return requiresEmailVerification: true
```

### User Signup (Invited Member)
```
POST /custom-signup {inviteToken} → Validate token → Create SuperTokens user →
Create PG User → Create MongoDB profile with inviter's org_id →
Auto-verify email → Mark invitation used → Return OK
```

### Profile Picture Upload
```
POST /media/profile-picture → Validate type/size → Upload to S3 →
Update PG user.profile_picture_url → Create UserMedia record →
Update MongoDB user.profile_picture_url → Return S3 URL
```

### Forum Post Creation
```
POST /forum/posts → Resolve user (session → PG → MongoDB) →
Create ForumPost in MongoDB → Log activity → Recalculate stats → Return post ID
```

---

## Architectural Patterns

1. **Dual-Database Sync**: SuperTokens ↔ PostgreSQL ↔ MongoDB. Email is the lookup key across all three.
2. **Dependency Injection**: `verify_session()` for auth, `get_db()` for DB sessions
3. **Service Layer**: Static methods separating business logic from endpoints
4. **Activity Tracking**: Every action creates UserActivity + triggers stats recalculation
5. **Async/Await Throughout**: All DB operations, email sending, S3 uploads
6. **Singleton DatabaseManager**: Single connection pool for both databases

---

## Security Features

- SuperTokens handles password hashing and sessions
- Email verification required for admins
- File type validation (whitelist) and size limits
- UUIDs for user IDs (vs sequential)
- Foreign key constraints with CASCADE
- Non-root container execution
- Token expiration (7-day invites, 1-hour resets)
- Role-based access (admin-only invitation sending, owner-only media deletion)
- CORS properly configured

---

## Logging

- **Library**: Loguru with InterceptHandler
- **Console**: Colored format output
- **File rotation**: 500MB, 10-day retention
- **Levels**: DEBUG (dev), INFO (prod)
- **Separate loggers**: uvicorn, fastapi

---

## Notable Technical Details

1. **MongoDB ObjectId vs SuperTokens ID**: Forum posts use MongoDB ID as author_id — can cause type confusion
2. **Hardcoded Production URLs**: Email links use `15.185.167.236:5173` — should be configurable
3. **Organization Auto-Creation**: Admin signup creates org by email domain, prevents duplicate admins per domain
4. **Stats Recalculation**: Weighted reputation scoring triggered after every activity
5. **Profile Picture Sync**: Deletes old S3 file, updates both PG + MongoDB

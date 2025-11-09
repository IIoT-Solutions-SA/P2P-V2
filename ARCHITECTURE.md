# P2P Manufacturing Knowledge Platform - Complete Architecture

## What It Is
A **peer-to-peer manufacturing knowledge-sharing platform** - basically LinkedIn + Stack Overflow + Case Study Library for manufacturers. Companies share manufacturing solutions (use cases), ask technical questions (forum), and connect with industry peers.

## Core Tech Stack
- **Backend**: FastAPI (Python) with dual databases (PostgreSQL + MongoDB)
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS
- **Auth**: SuperTokens (session-based, not JWT)
- **Storage**: AWS S3 (3 buckets: profile pics, forum media, use case media)
- **Deployment**: Docker Compose (5 services: postgres, mongodb, supertokens, backend, frontend)

---

## Architecture Highlights

### Dual-Database Pattern
**PostgreSQL**: Core user data (linked to SuperTokens), sessions, media tracking
**MongoDB**: Rich content (profiles, organizations, forum posts, use cases, activities)

**User Linking Chain**:
`SuperTokens session` → `supertokens_id` → PG `User.email` → Mongo `User.email` → Mongo `User._id` (ObjectId)

**Why Dual DB**: PG for ACID transactions (auth), Mongo for flexible schemas (nested documents like use cases with 20+ fields)

### Single-Database-Write Service Pattern
`UserService.create_user_with_profile()` atomically creates users in BOTH databases. If either fails → rollback.

---

## Complete Feature Set

### 1. Authentication & Organizations
- **Custom SuperTokens integration** (email/password + email verification)
- **Two signup flows**:
  - **Admin**: Creates organization (domain-based: `@iiotsolutions.sa` → IIoT Solutions org), requires email verification
  - **Member**: Join via invitation token, auto-verified
- **Single admin per organization** (enforced - raises error if duplicate admin signup)
- **Organization auto-grouping** by email domain
- **Session-based auth** (secure httpOnly cookies, no JWT)

### 2. Forum System (Technical Q&A)
- Create posts with title, content, category, tags, attachments (images/videos)
- Nested replies (threaded comments with `parent_reply_id`)
- Like posts/replies (stored in `liked_by` array + `upvotes` count)
- Mark best answers (contributor gets +30 bonus points)
- **Realistic view counting** (one view per user per post via UserActivity collection)
- Bookmark posts
- Edit/delete own posts (soft delete: `status = "deleted"`)
- Dynamic categories (generated from existing posts via MongoDB aggregation)
- **Top contributors leaderboard** (points: post=50, reply=20, best answer=+30, likes=5/3)

### 3. Use Case Library (Manufacturing Success Stories)
**Comprehensive schema** with 9 sections:
- Basic info: title, subtitle, factory, category, location (lat/lng for map)
- Business challenge: industry context, problems, financial loss
- Solution: vendor selection, tech components
- Implementation: timeline, budget, team structure, phases
- Results: quantitative metrics (baseline/current/improvement), ROI, annual savings
- Challenges & solutions
- Contact info
- Multiple images/videos
- **SEO-friendly URLs**: `/usecases/{company-slug}/{title-slug}`

**Two viewing modes**:
- **Cards Grid**: Paginated, filterable (category, search, sort)
- **Interactive Map**: Leaflet with marker clustering (click marker → popup with use case card)

### 4. Dashboard & Analytics
- User stats: questions asked, answers given, use cases submitted, bookmarks, reputation score, activity level
- Community activity feed (recent posts, replies, use cases from all users)
- Saved items (bookmarked posts/use cases)
- Draft management (auto-save incomplete posts)
- **Activity-based reputation** (recalculated from all activities)

### 5. Invitation System
- **Admin-only**: Send invitation to email → unique token generated
- Email sent with signup link: `{website_url}/join?token={token}`
- Token expires in 7 days
- Invited members auto-join inviter's organization
- Signup form prefilled with org details
- Track pending/used invitations

### 6. Media Management
- **Profile pictures**: Upload JPEG/PNG/WebP (5MB max) with crop editor
- **Forum attachments**: Images + videos (MP4/WebM, 50MB max)
- **Use case media**: Multiple images/videos per case
- **3 S3 buckets**: `p2p-prod-profile-images`, `p2p-prod-forum-media`, `p2p-prod-usecase-media`
- CloudFront CDN support (optional, falls back to direct S3 URLs)
- PostgreSQL `UserMedia` table tracks all uploads for auditing
- Cascade delete: user deleted → media deleted from S3 + DB

### 7. User Management
- View organization members (name, email, role, title, location, expertise tags)
- Admin: send invitations, view pending invites
- Edit profile: name, title, location, expertise tags, profile picture

---

## Database Schemas (Key Collections)

### PostgreSQL Tables
1. **users**: `id`, `supertokens_id` (unique), `email`, `name`, `role` (admin/member), `is_verified`, `profile_picture_url`
2. **user_media**: `id`, `user_id` (FK), `file_type`, `s3_key`, `s3_url`, `context_id` (post_id/usecase_id)
3. **system_config**: Key-value configs
4. **SuperTokens tables**: `emailpassword_users`, `session`, `emailverification_tokens`, etc.

### MongoDB Collections
1. **users**: Email, name, organization_id (ref), industry, location, expertise_tags, title, role, profile_picture_url
2. **organizations**: Name, domain (unique), industry_sector, size, country, city
3. **forum_posts**: Author_id, title, content, category, tags, attachments, best_answer_id, status, view_count, reply_count, upvotes, liked_by[], is_pinned
4. **forum_replies**: Post_id, author_id, content, parent_reply_id (nested), upvotes, liked_by[], is_best_answer, status
5. **use_cases**: 50+ fields including:
   - Basic: title, subtitle, factory_name, category, location {lat, lng}
   - Slugs: title_slug, company_slug
   - Rich content: executive_summary, business_challenge {industryContext, specificProblems[], financialLoss}, solution_details {vendorProcess, selectedVendor, technologyComponents[]}, implementation_details {methodology, totalBudget, phases[]}, results {quantitativeResults[], roiPercentage, annualSavings}, challenges_and_solutions[]
   - Media: images[], videos[]
   - Meta: published, featured, status, view_count, like_count, liked_by[]
6. **user_activities**: user_id, activity_type (question/answer/like/bookmark/view/use_case), target_id, created_at
7. **user_stats**: user_id, questions_asked, answers_given, best_answers, use_cases_submitted, bookmarks_saved, reputation_score, activity_level (%)
8. **user_bookmarks**: user_id, target_type (forum_post/use_case), target_id, target_title
9. **invitations**: email, token (UUID), invited_by_id, expires_at, used, created_at
10. **draft_posts**: user_id, title, content, post_type, category, tags (forum drafts only)
11. **use_case_drafts**: user_id, current_step (1-7 wizard tracking), all UseCase fields as Optional (50+ fields for partial saves), created_at, updated_at

---

## API Endpoints (All Routes)

### Auth (`/api/v1/auth`)
- `POST /custom-signup` - Signup (admin or member via invite token)
- `POST /custom-signin` - Login (blocks if email not verified)
- `POST /signout` - Logout
- `POST /user/email/verify` - Verify email with token
- `POST /forgot-password` - Request password reset email
- `POST /reset-password` - Reset password with token from email
- `GET /me` - Get current user + organization
- `PUT /profile` - Update profile (name, title, location, expertise tags)
- `PUT /email` - Change email
- `PUT /password` - Change password
- `GET /users/organization` - Get all members of user's org

### Forum (`/api/v1/forum`)
- `POST /posts` - Create post
- `GET /posts` - List posts (filter by category, paginated)
- `GET /posts/{post_id}` - Get post detail with replies (increments view count once per user)
- `PUT /posts/{post_id}` - Update own post
- `DELETE /posts/{post_id}` - Soft delete own post
- `POST /posts/{post_id}/like` - Toggle like
- `POST /posts/{post_id}/bookmark` - Toggle bookmark
- `POST /posts/{post_id}/replies` - Add reply (supports nested via parent_reply_id)
- `POST /replies/{reply_id}/like` - Toggle like on reply
- `GET /categories` - Get categories with post counts
- `GET /stats` - Get forum stats (total topics, active members, helpful answers)
- `GET /contributors` - Get top contributors leaderboard
- `GET /bookmarks` - Get user's bookmarked posts

### Use Cases (`/api/v1/use-cases`)
- `POST /` - Submit use case
- `GET /` - List use cases (paginated, filterable, sortable)
- `GET /by-id/{use_case_id}` - Get by MongoDB ID (for editing)
- `GET /{company_slug}/{title_slug}` - Get by slug (increments view count)
- `PUT /{use_case_id}` - Update own use case
- `DELETE /{use_case_id}` - Soft delete
- `POST /{company_slug}/{title_slug}/like` - Toggle like
- `POST /{company_slug}/{title_slug}/bookmark` - Toggle bookmark
- `GET /bookmarks` - Get user's bookmarked use cases
- `GET /categories` - Get categories with counts
- `GET /stats` - Get stats (total cases, contributing companies, success stories)
- `GET /contributors` - Get top contributing companies
- `POST /drafts` - Save/update use case draft (supports partial data, multiple drafts per user)
- `GET /drafts` - List user's use case drafts
- `GET /drafts/{draft_id}` - Get specific draft by ID
- `DELETE /drafts/{draft_id}` - Delete draft
- `POST /drafts/{draft_id}/publish` - Publish draft as use case (validates required fields)
- `GET /drafts` - List user's use case drafts
- `GET /drafts/{draft_id}` - Get specific draft by ID
- `DELETE /drafts/{draft_id}` - Delete draft
- `POST /drafts/{draft_id}/publish` - Publish draft as use case (validates required fields)

### Dashboard (`/api/v1/dashboard`)
- `GET /stats` - Get user stats
- `GET /activities` - Get community activity feed
- `GET /bookmarks` - Get user's bookmarks
- `POST /bookmark` - Add bookmark
- `GET /drafts` - Get user's draft posts
- `POST /drafts` - Create draft
- `PUT /drafts/{draft_id}` - Update draft
- `DELETE /drafts/{draft_id}` - Delete draft
- `POST /recalculate-stats` - Trigger stats recalculation

### Invitations (`/api/v1/invites`)
- `POST /send` - Send invitation (admin only)
- `GET /validate/{token}` - Validate token
- `GET /all` - Get all invitations (admin sees all, users see own)
- `GET /pending` - Get pending invitations
- `POST /mark-used/{token}` - Mark as used (internal, called by signup)
- `DELETE /{invitation_id}` - Cancel invitation

### Media (`/api/v1/media`)
- `POST /profile-picture` - Upload profile picture (5MB max, deletes old)
- `POST /forum-attachment` - Upload forum attachment (images/videos 50MB max)
- `POST /usecase-media` - Upload use case media (up to 10 files)
- `DELETE /{media_id}` - Delete media file
- `GET /user/{user_id}` - Get user's media files

### Health
- `GET /api/v1/health` - Health check

---

## Frontend Structure

### Pages
1. **LandingPage**: Hero, features, stats, recent activity, CTAs
2. **Signup**: Admin signup (email verification required)
3. **MemberSignup**: Invitation-based signup (prefilled, auto-verified)
4. **Login**: Email/password (blocks if not verified)
5. **ForgotPassword**: Request password reset email
6. **ResetPassword**: Reset password with token from email
7. **EmailVerificationPending**: "Check your email" message
8. **EmailVerificationSuccess**: Verification complete
9. **Dashboard**: User stats, activity feed, bookmarks, use case drafts
10. **Forum**: Post listing + detail view (expandable in-page)
11. **UseCases**: Cards grid + interactive map (toggle tabs)
12. **UseCaseDetail**: Full case study with tabs (Overview, Challenge, Solution, Implementation, Results, etc.)
13. **SubmitUseCase**: 7-step wizard form with dual autosave (localStorage + server), manual "Save as Draft" button, draft resume from URL, "Start New Use Case" feature for managing multiple drafts
14. **UserManagement**: Org members list + send invitations (admin)
15. **Connect**: Networking page (future/placeholder)

### Key Components
- **Navigation**: Desktop (top nav) + mobile (bottom nav)
- **ProtectedRoute**: Session check wrapper
- **CreatePostModal**: Forum post creation
- **ProfilePictureEditor**: Upload, crop, resize
- **InteractiveMap**: Leaflet with marker clustering
- **LocationPicker**: Map-based lat/lng selector
- **MediaGallery**: Image/video carousel
- **FileDropZone**: Drag-and-drop upload
- **AuthContext**: Global auth state (user, org, isAuthenticated)

### Routing
- `/` - Landing
- `/signup` - Admin signup
- `/join?token={token}` - Member signup
- `/login` - Login
- `/dashboard` - Dashboard (protected)
- `/forum` - Forum (protected)
- `/usecases` - Use case library (protected)
- `/usecases/:companySlug/:titleSlug` - Use case detail (protected)
- `/submit` - Submit use case (protected)
- `/users` - User management (protected)
- `/connect` - Networking (protected)
- `/verify-email` - Email verification pending
- `/auth/verify-email` - Email verification callback

---

## Deployment (Docker Compose)

### Services
1. **postgres** (port 5432): Two databases (`p2p_sandbox`, `supertokens`)
2. **mongodb** (port 27017): Database `p2p_sandbox`
3. **supertokens** (port 3567): Auth core service
4. **backend** (port 8000): FastAPI with Alembic migrations on startup
5. **frontend** (port 5173): Vite dev server

### Startup Sequence
1. postgres + mongodb start
2. supertokens waits for postgres health check
3. backend waits for postgres + mongodb health checks → runs migrations → starts uvicorn
4. frontend waits for backend health check → starts Vite

### Environment Detection
- **Production**: IP `15.185.167.236`
- **Local**: `localhost`
- **Demo**: `peerlink.sa` (via hosts file entry)

Frontend auto-detects via `window.location.hostname`

---

## Unique Implementation Details

1. **Dual-database sync**: `UserService.create_user_with_profile()` atomically writes to PG + Mongo
2. **Single admin enforcement**: Checks for existing admin on domain before allowing admin signup
3. **Invite-based onboarding**: Members auto-join inviter's org, skip email verification
4. **Realistic view counting**: UserActivity tracks who viewed what (one view per user lifetime)
5. **Soft deletes**: Forum posts/use cases marked as "deleted", not physically removed
6. **Slug-based URLs**: `/usecases/iiot-solutions/oee-tracking-iot-kit` (SEO-friendly)
7. **Nested forum replies**: Unlimited depth via `parent_reply_id`
8. **Activity-based reputation**: Points system (post=50, reply=20, best answer=+30, likes=5/3)
9. **Dynamic categories**: Generated from existing posts via MongoDB aggregation
10. **S3 with MongoDB URLs**: Files in S3, URLs in Mongo docs, metadata in PG UserMedia
11. **Interactive map clustering**: Leaflet with automatic marker clustering
12. **Multi-stage use case wizard**: 9 steps with draft auto-save
13. **Custom email verification**: Override SuperTokens default with branded emails
14. **Session-based auth**: httpOnly cookies (not JWT) for better security
15. **Profile picture crop**: Canvas API crop + resize before upload
16. **Bookmarking**: Separate collection (not embedded in docs) for easier querying
17. **Domain-based org grouping**: Auto-create/join org by email domain
18. **Comprehensive seeding**: 24 users, 34 use cases, forum posts, all verified
19. **Mobile-first responsive**: Bottom nav (mobile), top nav (desktop), adaptive layouts
20. **TypeScript strict mode**: Full type safety with Zod runtime validation

---

## Seeding Scripts

**Run from docker directory**:
```bash
docker-compose -f development_docker-compose.yml exec backend python scripts/seed_all.py
```

**Seeds**:
- 18 demo users (various companies)
- 6 IIoT Solutions team (Aadil as admin, 5 members)
- 34 use cases (15 basic + 19 comprehensive)
- Forum posts + replies
- User activities
- All users email-verified

**Team seeding strategy**:
1. Create Aadil (admin) → establishes org
2. Get org_id from Aadil's Mongo profile
3. Create 5 members → initially without org
4. Post-creation: Update each member's `organization_id` via Beanie `.save()`

---

## Key Libraries

**Backend**:
- FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic, Asyncpg (PG async driver)
- Motor (Mongo async driver), Beanie (Mongo ODM)
- SuperTokens-Python, Boto3 (S3), FastAPI-Mail, Tenacity (retry logic)

**Frontend**:
- React 19, React-Router-DOM 7, Vite 7, TypeScript 5, Tailwind CSS 4
- SuperTokens-Auth-React, React-Hook-Form, Zod
- Leaflet + react-leaflet + leaflet.markercluster
- Lucide-React (icons), Radix UI (headless components)

---

## Data Flow Examples

### Example 1: User Signup (Admin)
1. User fills form on `/signup`
2. Frontend: POST `http://localhost:8000/api/v1/auth/custom-signup`
   ```json
   {
     "email": "john@acme.com",
     "password": "secure123",
     "firstName": "John",
     "lastName": "Doe",
     "companyName": "Acme Corp",
     "industrySector": "Automotive",
     "companySize": "medium",
     "city": "Riyadh",
     "title": "CTO"
   }
   ```
3. Backend: `supertokens_auth.py` → `post_signup()`
4. Check `inviteToken` → None → role = "admin"
5. Call `sign_up("public", email, password)` → SuperTokens creates user → returns `supertokens_id`
6. Extract domain: `acme.com`
7. Check MongoDB for Organization with `domain = "acme.com"` → Not found
8. Create Organization: `{name: "Acme", domain: "acme.com", industry_sector: "Automotive", size: "medium", city: "Riyadh"}`
9. Call `UserService.create_user_with_profile(db, supertokens_id, email, profile_data)`
10. Create PostgreSQL User: `{supertokens_id, email, name: "John Doe", role: "admin"}`
11. Create MongoDB User: `{email, name: "John Doe", organization_id: <org_id>, industry_sector: "Automotive", title: "CTO", role: "admin"}`
12. Send verification email via `EmailVerificationService` → token generated → email sent
13. Return: `{status: "OK", requiresEmailVerification: true, email: "john@acme.com"}`
14. Frontend: Redirect to `/verify-email` → shows "Check your email" message
15. User clicks link in email → SuperTokens verifies token → email marked as verified
16. User can now login

### Example 2: Forum Post Creation with Like
1. User on `/forum` clicks "Create Post" button
2. Modal opens → user fills form: `{title: "How to reduce scrap?", content: "...", category: "Quality Control", tags: ["quality", "waste"]}`
3. Submit → Frontend: POST `http://localhost:8000/api/v1/forum/posts`
   ```json
   {
     "title": "How to reduce scrap?",
     "content": "We're seeing 5% scrap rate...",
     "category_id": "Quality Control",
     "tags": ["quality", "waste"]
   }
   ```
4. Backend: `forum.py` → `create_forum_post()` (protected with `verify_session()`)
5. Extract `supertokens_user_id` from session
6. Lookup PostgreSQL User by `supertokens_id` → get `email`
7. Lookup MongoDB User by `email` → get `_id` (ObjectId)
8. Create ForumPost: `{author_id: <mongo_user_id>, title, content, category: "Quality Control", tags: [...], created_at: now()}`
9. Insert into MongoDB → get `post_id`
10. Log activity: `UserActivityService.log_activity(user_id, "question", post_id, title, "Quality Control")`
11. Return: `{id: <post_id>}`
12. Frontend: Close modal, refresh post list

**Later: Another user likes the post**
1. User clicks like button on post card
2. Frontend: POST `http://localhost:8000/api/v1/forum/posts/{post_id}/like`
3. Backend: `forum.py` → `like_forum_post()` (protected)
4. Extract `supertokens_user_id` from session → resolve to `mongo_user_id`
5. Call `ForumService.toggle_like(user_supertokens_id, post_id, "post", db)`
6. Find ForumPost by `_id`
7. Check if `mongo_user_id` in `post.liked_by` array
8. If not: Add to array, increment `upvotes` by 1
9. Save post
10. Return: `{liked: true, likes: 15}`
11. Frontend: Update like button state (filled heart), update likes count

### Example 3: Use Case Submission with Media
1. User on `/submit` fills multi-step form (9 steps)
2. Step 8: User selects 3 images from local disk
3. Frontend: Create FormData, append files + usecase_id (temporary, generated client-side)
4. POST `http://localhost:8000/api/v1/media/usecase-media`
   ```
   FormData: files[0], files[1], files[2], usecase_id: "temp-123"
   ```
5. Backend: `media.py` → `upload_usecase_media()` (protected)
6. Validate files (JPEG/PNG, 5MB each)
7. For each file:
   - Generate S3 key: `usecase-images/temp-123/{uuid}.jpg`
   - Upload to S3 bucket: `p2p-prod-usecase-media`
   - Get URL: `https://p2p-prod-usecase-media.s3.me-south-1.amazonaws.com/usecase-images/temp-123/{uuid}.jpg`
   - Create UserMedia record in PostgreSQL
8. Return: `{success: true, files: [{url, filename, type, size}, ...]}`
9. Frontend: Store URLs in form state (`images: ["https://...", "https://...", "https://..."]`)
10. User completes form, clicks "Submit"
11. Frontend: POST `http://localhost:8000/api/v1/use-cases/`
    ```json
    {
      "title": "Predictive Maintenance with IoT",
      "subtitle": "Reducing downtime by 30%",
      "factoryName": "Acme Corp",
      "category": "Predictive Maintenance",
      "city": "Riyadh",
      "latitude": 24.7136,
      "longitude": 46.6753,
      "industryContext": "Automotive manufacturing...",
      "specificProblems": ["Unplanned downtime", "High maintenance costs"],
      "financialLoss": "$500K/year",
      "selectedVendor": "IIoT Solutions",
      "technologyComponents": ["IoT sensors", "ML algorithms"],
      "implementationTime": "6 months",
      "totalBudget": "$200K",
      "quantitativeResults": [{metric: "Downtime", baseline: "100 hrs/month", current: "70 hrs/month", improvement: "30%"}],
      "roiPercentage": "150%",
      "images": ["https://...", "https://...", "https://..."],
      "contactPerson": "John Doe",
      "contactTitle": "CTO"
    }
    ```
12. Backend: `usecases.py` → `submit_new_use_case()` (protected)
13. Resolve user → get `mongo_user_id`
14. Generate slugs: `title_slug = "predictive-maintenance-with-iot"`, `company_slug = "acme-corp"`
15. Create UseCase document with all fields → insert into MongoDB → get `usecase_id`
16. Update UserMedia records: set `context_id = <real_usecase_id>`
17. Update UseCase: set images array with URLs (already there from request)
18. Log activity: `UserActivityService.log_activity(user_id, "use_case", usecase_id, title, category)`
19. Recalculate stats: `UserActivityService.recalculate_user_stats(user_id)` → increments `use_cases_submitted`
20. Return: `{status: "success", id: <usecase_id>}`
21. Frontend: Redirect to `/usecases/acme-corp/predictive-maintenance-with-iot`

---

## Architecture Patterns Summary

### Service Layer
- **UserService**: Dual-DB user creation/management
- **ForumService**: Forum CRUD, like toggles, reply management
- **UseCaseSubmissionService**: Use case CRUD, slug generation
- **UserActivityService**: Activity logging, stats calculation, bookmarks, drafts
- **InvitationService**: Invitation creation, validation, tracking
- **EmailService**: SMTP email sending (invites, verification)
- **S3Service**: File uploads, deletions, URL generation

### Repository Pattern
All services interact with databases through:
- SQLAlchemy sessions (PostgreSQL)
- Beanie document models (MongoDB)

### Dependency Injection
FastAPI `Depends()` used for:
- Database sessions: `get_db()`
- Session verification: `verify_session()`
- User resolution: extract `supertokens_id` → resolve to PG user

### Middleware Stack
1. CORS middleware (SuperTokens headers)
2. SuperTokens middleware (handles `/auth/*` routes)
3. Session verification (per-endpoint via `Depends(verify_session)`)

---

## Security Features

1. **Email verification required** for admin signups
2. **Single admin per org** (prevents privilege escalation)
3. **Invitation token validation** (expiry, one-time use)
4. **Session-based auth** (httpOnly cookies, CSRF protection)
5. **Authorization checks** (users can only edit/delete own content)
6. **Role-based access** (admin-only endpoints like send invites)
7. **Soft deletes** (audit trail, data recovery)
8. **S3 file validation** (type, size limits)
9. **Password hashing** (bcrypt via Passlib)
10. **CORS configuration** (whitelist origins)

---

## Performance Optimizations

1. **MongoDB indexing** on email, category, tags, created_at, domain
2. **Geo2d index** for location-based queries
3. **Async database drivers** (asyncpg, motor) for non-blocking I/O
4. **Connection pooling** (SQLAlchemy, Motor)
5. **Presigned S3 URLs** (optional, for private objects)
6. **CloudFront CDN** (optional, for faster media delivery)
7. **Pagination** (all list endpoints use limit/skip)
8. **Aggregation pipelines** (MongoDB for categories, stats, leaderboards)
9. **Lazy loading** (frontend loads data on-demand)
10. **Debounced draft saves** (reduces API calls)

---

## Known Limitations & Future Enhancements

### Current Limitations
1. **No real-time updates** (no WebSockets for live forum updates)
2. **No full-text search** (basic MongoDB text search, not Elasticsearch)
3. **No email notifications** (for new replies, mentions, etc.)
4. **No user-to-user messaging** (Connect page is placeholder)
5. **No export functionality** (for use cases, forum posts)
6. **No analytics dashboard** (for admins to track org activity)
7. **No API rate limiting** (could be DoS vulnerable)
8. **No API versioning strategy** (all endpoints v1)
9. **No automated tests** (no pytest, no frontend tests)
10. **No CI/CD pipeline** (manual deployment)

### Planned Enhancements (Based on Code Structure)
1. **Connect feature**: User-to-user messaging, connection requests
2. **Advanced search**: Elasticsearch integration for full-text search
3. **Email notifications**: New replies, mentions, weekly digests
4. **Export to PDF**: Use case export as PDF reports
5. **Analytics dashboard**: Org-level activity tracking
6. **API rate limiting**: Redis-based rate limiter
7. **Automated testing**: Pytest for backend, Vitest for frontend
8. **CI/CD**: GitHub Actions for automated builds/deploys
9. **Monitoring**: Sentry for error tracking, Prometheus for metrics
10. **Mobile app**: React Native app using same API

---

## Troubleshooting Guide

### Common Issues

**Backend won't start**:
- Check PostgreSQL/MongoDB connections (wait scripts in Dockerfile)
- Verify Alembic migrations ran successfully
- Check env vars (DATABASE_URL, MONGODB_URL)

**Email verification not working**:
- Check SMTP credentials in backend `.env`
- Verify `WEBSITE_DOMAIN` points to frontend URL
- Check SuperTokens email delivery override

**Profile picture upload fails**:
- Verify AWS credentials (ACCESS_KEY, SECRET_KEY)
- Check S3 bucket permissions
- Verify file size < 5MB

**Forum view count inflation**:
- React StrictMode double-renders in dev (expected)
- Production mode should have realistic counts (one per user)

**Use case map not showing markers**:
- Verify use cases have valid lat/lng coordinates
- Check Leaflet CSS imported in main.tsx
- Check browser console for Leaflet errors

**Session expired errors**:
- SuperTokens session expired (default 7 days)
- User needs to re-login
- Check `SUPERTOKENS_CONNECTION_URI` is accessible

---

This document provides a complete overview of the P2P Manufacturing Knowledge Platform architecture, implementation details, and operational knowledge.

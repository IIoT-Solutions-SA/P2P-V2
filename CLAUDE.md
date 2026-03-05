# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# P2P Manufacturing Knowledge Platform

## Project Overview
P2P (peer-to-peer) Manufacturing Knowledge Platform that connects manufacturers, facilitates knowledge sharing, and enables collaborative problem-solving in the manufacturing industry.

## Technical Stack

### Frontend (`p2p-frontend-app/`)
- **Framework**: React 19 with TypeScript (~13,475 lines across 51 TSX files)
- **Build Tool**: Vite 7
- **State Management**: React Context/Hooks
- **Routing**: React Router DOM v7
- **Styling**: Tailwind CSS 4.1 + Radix UI headless components
- **API Client**: Native Fetch API (with `credentials: 'include'` for session cookies)
- **Forms**: React Hook Form + Zod validation
- **Maps**: Leaflet with react-leaflet + MarkerCluster
- **Icons**: Lucide React

### Backend (`p2p-backend-app/`)
- **Framework**: FastAPI (Python)
- **Databases**:
  - PostgreSQL (user core data, sessions via SuperTokens)
  - MongoDB (extended profiles, use cases, forums, organizations)
- **Authentication**: SuperTokens (EmailPassword recipe with email verification)
- **ORM/ODM**: SQLAlchemy (async) for PostgreSQL, Beanie (Motor) for MongoDB
- **Migrations**: Alembic for PostgreSQL schema migrations
- **API Documentation**: Auto-generated OpenAPI/Swagger at `/docs`

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Development Environment**: WSL2 on Windows (note: git operations slow on `/mnt/c`)
- **Branch Strategy**: `hamza-backend` (working branch), `main` (PRs), `demo-peerlink` (demo setup with peerlink.sa)

## Architecture Overview

### Dual-Database Pattern
- **PostgreSQL**: Core user records (linked to SuperTokens via `supertokens_id`), system configs
- **MongoDB**: Rich profiles, organizations, use cases, forums, invitations, user activities
- **Synchronization**: User creation flows through `UserService.create_user_with_profile()` which creates records in both databases

### Authentication Flow
1. **SuperTokens** handles auth/session management (`/api/v1/auth/*`)
2. Custom signup endpoint (`/api/v1/auth/custom-signup`) creates users in SuperTokens + both databases
3. Email verification required for admin signups, auto-verified for invited members
4. Session middleware protects endpoints

### User Roles & Organizations
- **Admin**: First signup from a domain creates organization and becomes admin
- **Member**: Invited users join existing organization via invitation token
- Organizations linked by email domain (e.g., `@iiotsolutions.sa`)

### Frontend Environment Detection
`p2p-frontend-app/src/config/environment.ts` automatically detects:
- Production server: `15.185.167.236`
- Local development: `localhost`
- Demo mode: `peerlink.sa` (requires hosts file entry)

## Development Commands

### Docker Deployment (Recommended)
**Important**: Always navigate to `docker/` directory first:
```bash
cd docker
```

**Development Mode (from docker directory):**
```bash
docker-compose -f development_docker-compose.yml up --build
```
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Production Mode (from docker directory):**
```bash
docker-compose up --build
```
- Frontend: http://15.185.167.236:5173
- Backend API: http://15.185.167.236:8000

**Stop & Clean:**
```bash
docker-compose down          # Stop services
docker-compose down -v       # Stop and remove all data (volumes)
```

### Database Seeding
**Complete seed (fresh demo setup):**
```bash
cd docker
docker-compose -f development_docker-compose.yml exec backend python scripts/seed_all.py
```
This seeds:
- 24 users (18 demo + 6 IIoT Solutions team)
- 34 use cases (15 + 19 comprehensive)
- Forums & activities
- All users email-verified

**Individual seed scripts:**
- `seed_db_users.py` - 18 demo users
- `seed_team_members.py` - 6 IIoT Solutions team (Aadil as admin, rest as members in same org)
- `seed_usecases.py` - 15 basic use cases
- `seed_forums.py` - Forum posts
- `seed_user_activities.py` - User activities
- `verify_existing_users.py` - Mark all users as email verified

### Backend Development (Without Docker)
```bash
cd p2p-backend-app
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Database migrations:**
```bash
cd p2p-backend-app
alembic upgrade head                    # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

### Frontend Development (Without Docker)
```bash
cd p2p-frontend-app
npm install
npm run dev              # Start dev server (port 5173)
npm run build            # Production build
npm run lint             # ESLint
npm run typecheck        # TypeScript checks
```

## Key Backend Architecture

### Service Layer Pattern (~2,433 lines total)
- `UserService` (`database_service.py`): Dual-database user creation/management
- `ForumService` (`forum_service.py`): Forum CRUD operations
- `UseCaseSubmissionService` (`usecase_service.py`): Use case management with slug generation
- `InvitationService` (`invitation_service.py`): Member invitation flow (7-day token expiry)
- `S3Service` (`s3_service.py`): File uploads (3 buckets: profile pics, forum media, use case media)
- `EmailService` (`email_service.py`): Invitation & welcome emails via Gmail SMTP
- `EmailVerificationService` (`email_verification_service.py`): Custom verification emails
- `PasswordResetService` (`password_reset_service.py`): Custom password reset emails
- `UserActivityService` (`user_activity_service.py`): Activity logging, stats & reputation scoring

### Database Connections
- `DatabaseManager` (singleton): Manages PostgreSQL + MongoDB connections with retry logic
- Dependency injection via `get_db()` for PostgreSQL sessions
- MongoDB accessed via Beanie document models

### API Structure
```
app/
├── api/v1/
│   ├── api.py                  # Router aggregation (all endpoints mounted here)
│   └── endpoints/
│       ├── supertokens_auth.py # Custom signup, email verification (250+ lines)
│       ├── auth.py             # Session info, user profiles, password/email change (387 lines)
│       ├── invites.py          # Member invitations (259 lines)
│       ├── forum.py            # Forum posts/replies/likes/bookmarks (250+ lines)
│       ├── usecases.py         # Use case CRUD, likes, bookmarks (250+ lines)
│       ├── media.py            # File uploads to S3 (484 lines)
│       ├── dashboard.py        # Stats, activities, drafts, bookmarks (100+ lines)
│       └── health.py           # Health check endpoint
├── core/
│   ├── database.py             # DatabaseManager singleton (PG + MongoDB)
│   ├── supertokens.py          # SuperTokens init with custom email overrides
│   ├── config.py               # Settings from env vars (S3 buckets, CORS, domains)
│   └── logging.py              # Loguru configuration (500MB rotation, 10-day retention)
├── models/
│   ├── pg_models.py            # SQLAlchemy: User, UserSession, UserMedia, SystemConfig
│   └── mongo_models.py         # Beanie: User, Org, ForumPost, ForumReply, UseCase, etc. (318 lines)
├── services/                   # Business logic (9 service files, 2,433 lines)
└── schemas/                    # Pydantic request/response models
```

## Important Implementation Details

### Custom Signup Flow (`supertokens_auth.py`)
1. Check for `inviteToken` → determines role (admin vs member)
2. Explicit `role` parameter allowed for seeding scripts
3. Creates SuperTokens user
4. Calls `UserService.create_user_with_profile()` to create dual-DB records
5. Organization assignment:
   - With invite token: joins inviter's organization
   - Admin without token: creates/joins org by email domain
   - Member without token (seeding): needs manual MongoDB update

### Email Verification
- Admins: verification email sent, must verify before first login
- Invited members: auto-verified (they already received invite email)
- Seeding: `verify_existing_users.py` bulk-verifies all users

### Team Member Seeding Strategy
1. Create Aadil (admin) first → establishes IIoT Solutions organization
2. Get `organization_id` from Aadil's MongoDB record
3. Create other 5 members → initially created without org
4. Post-creation: update each member's `organization_id` in MongoDB via Beanie `.save()`
5. Result: All 6 in same organization without modifying invitation flow

## Git Workflow

### Branch Strategy
- `hamza-backend`: Primary working branch
- `main`: Production branch (for PRs)
- `demo-peerlink`: Demo branch with peerlink.sa custom domain setup

### Merging Changes
To bring changes from `hamza-backend` into `demo-peerlink`:
```bash
git checkout demo-peerlink
git merge hamza-backend
git push origin demo-peerlink
```

### Commit Guidelines
- Always use `git add .` (not individual files)
- Check `git log` for project's commit style
- Write detailed commit messages with bullet points
- Include technical details and user impact
- Use `git push origin <branch-name>`

## Demo Setup (peerlink.sa)

For professional demos, the `demo-peerlink` branch includes:
1. **Hosts file entry**: `127.0.0.1 peerlink.sa`
   - Windows: `C:\Windows\System32\drivers\etc\hosts`
   - Mac: `/etc/hosts`
2. **Vite config**: Allows `peerlink.sa` hostname, port 80
3. **Environment detection**: Smart hostname-based URL configuration
4. **Docker config**: CORS, cookie domain, API/website URLs for peerlink.sa

Access at: http://peerlink.sa (port 80)

## Common Gotchas

- **WSL2 Performance**: Git operations very slow on `/mnt/c/` - use native Windows PowerShell for git when possible
- **Docker context**: Must run docker commands from `docker/` directory
- **SuperTokens database**: Created via Docker init script (`docker/init-db.sql`)
- **Profile pictures**: Require AWS S3 credentials in `.env`
- **CORS**: Development mode uses `http://localhost:5173`, production uses IP `15.185.167.236`
- **Email verification**: Required for admin signups, can be bypassed in seeding

## Environment Variables

### Backend (`.env` in `p2p-backend-app/`)
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
MONGODB_URL=mongodb://host:27017
SUPERTOKENS_CONNECTION_URI=http://supertokens:3567
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=me-south-1
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (`.env.development` or `.env.production`)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_WEBSITE_BASE_URL=http://localhost:5173
```
Note: Auto-detected if not set (see `environment.ts`)

## Testing Credentials
After seeding:
- Admin: `aadil@iiotsolutions.sa` / `password123`
- Demo users: `user1@example.com` through `user18@example.com` / `password123`
- All users email-verified after running seed scripts

## Session Logs

Development session logs are stored in `docs/Logs/` and tracked in git. Each session creates a detailed log documenting work completed, files changed, and issues encountered. See `docs/Logs/` for the full history.

## Reputation Scoring System

Points are calculated by `UserActivityService.recalculate_user_stats()`:
- 2 pts per question asked
- 3 pts per answer given
- 15 pts per best answer
- 10 pts per use case submitted
- 1 pt per upvote received
- Activity level: based on 30-day rolling window, capped at 100%

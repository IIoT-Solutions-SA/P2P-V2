# Backend Docs Exploration Log

**Date:** 2026-03-05
**Session:** 005
**Agent:** Backend Docs Explorer

## Objective

Comprehensive exploration of the `backend docs/` directory — all implementation story docs, deployment guides, configuration references, and technical specifications.

## Summary

The backend docs folder contains **27 markdown files** documenting the entire backend implementation journey from Stories 3-20, plus deployment guides, AWS S3 configuration, use case field specs, and user deletion procedures. This is the detailed development history and technical reference for the P2P backend.

---

## Directory Structure

```
backend docs/
├── changes.md                              # AWS deployment changes log
├── changes_needed.md                       # Environment configuration fixes
├── PRODUCTION_USE_CASE_DEPLOYMENT.md       # Use case deployment strategy
├── S3_BUCKET_CONFIGURATION.md              # AWS S3 bucket setup
├── use-case-fields-documentation.md        # Complete use case field specifications
├── user-deletion-process.md                # Complete user deletion across databases
├── story-03-*.md                           # Backend API setup
├── story-04-*.md                           # Database configuration
├── story-05-*.md                           # Authentication integration
├── story-06-*.md                           # Docker containerization
├── story-08-*.md                           # Organization signup flow
├── story-09-*.md                           # Forum replies & interactions
├── story-10-*.md                           # Use case submission
├── story-11-*.md                           # Use case CRUD operations
├── story-12-*.md                           # Draft system
├── story-13-*.md                           # Profile management
├── story-14-*.md                           # (if exists)
├── story-15-*.md                           # Invitation system
├── story-16-*.md                           # Comprehensive seeding
├── story-17-*.md                           # Media upload system
├── story-18-*.md                           # Mobile responsiveness / fixes
├── story-19-*.md                           # (if exists)
└── story-20-*.md                           # Email verification
```

---

## Key Backend Systems Documented

### 1. Authentication & Authorization (Stories 5, 8, 15, 20)

- **SuperTokens Integration**: EmailPassword recipe with email verification
- **Custom Signup Flow**: Role-based (admin vs member) account creation
- **Organization System**: Domain-based org creation, member invitations
- **Email Verification**: Required for admins, auto-verified for invited members
- **Session Management**: Secure cookie-based sessions with automatic refresh
- **Critical Implementation**: Role assignment based on invitation token presence

### 2. Database Architecture (Story 4)

- **Dual-Database Pattern**:
  - PostgreSQL (port 5432): User accounts, sessions, system configs
  - MongoDB (port 27017): Rich profiles, forums, use cases, activities
  - SuperTokens PostgreSQL: Authentication data (separate database)
- **Connection Management**: DatabaseManager singleton with retry logic, pool management
- **Alembic Migrations**: Async migration system for PostgreSQL schema changes
- **Data Synchronization**: Custom flows ensuring consistency across both databases

### 3. Complete API Endpoints

**Authentication** (`/api/v1/auth/`):
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/custom-signup` | Organization registration with custom fields |
| POST | `/custom-signin` | Enhanced sign-in with session management |
| GET | `/me` | Current user profile with org context |
| PUT | `/profile` | Update user profile info |
| PUT | `/email` | Change email (requires password verification) |
| PUT | `/password` | Change password (requires current password) |

**Forum** (`/api/v1/forum/`):
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/posts` | Create, list, filter forum posts |
| GET | `/posts/{id}` | Detailed post with nested comments |
| POST | `/posts/{id}/like` | Toggle likes (one per user) |
| POST | `/posts/{id}/replies` | Create replies with nesting support |
| POST | `/replies/{id}/like` | Like replies |
| GET/POST | `/bookmarks` | Save/unsave posts |
| GET | `/categories` | Dynamic categories with counts |
| POST/DELETE | Various | Complete CRUD for forums |

**Use Cases** (`/api/v1/use-cases/`):
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List with category, search, sort, pagination |
| GET | `/categories` | Categories with post counts |
| GET | `/stats` | Platform statistics |
| GET | `/contributors` | Top companies by contribution |
| GET | `/{company_slug}/{title_slug}` | Detailed view by slugs |
| POST | `/` | Submit new use case |
| PUT | `/{id}` | Edit use case |
| DELETE | `/{id}` | Delete use case |
| GET/POST | `/bookmarks` | User-saved use cases |

**Dashboard** (`/api/v1/dashboard/`):
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/stats` | User statistics (posts, answers, bookmarks, reputation) |
| GET | `/activities` | Recent community activities |
| GET | `/bookmarks` | Saved items |
| GET/POST/PUT/DELETE | `/drafts` | Draft management |

**Media** (`/api/v1/media/`):
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/profile-picture` | Upload profile picture to S3 |
| POST | `/forum-attachment` | Forum media attachment |
| POST | `/usecase-media` | Use case media upload (multiple) |
| DELETE | `/{media_id}` | Delete user's media |
| GET | `/user/{user_id}` | User's media files |

**Invitations** (`/api/v1/invites/`):
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/send` | Send email invitation with token |
| GET | `/validate/{token}` | Validate invitation token |
| GET | `/pending` | List pending invitations |
| DELETE | `/{id}` | Cancel invitation |

### 4. Data Models

**PostgreSQL Models** (`app/models/pg_models.py`):
- `User`: Email, name, role, organization ID, profile picture URL
- `UserSession`: Session management with token indexing
- `SystemConfig`: Key-value configuration storage
- `UserMedia`: Track all uploaded media with S3 keys and ownership

**MongoDB Models** (`app/models/mongo_models.py`):
- `User`: Extended profile with industry, location, expertise tags, organization_id
- `Organization`: Company info, domain, size, location
- `ForumPost`: Title, content, category, author, likes, replies, status, attachments
- `ForumReply`: Nested reply structure with likes, best answer marking
- `UseCase`: Comprehensive case studies with 50+ fields
- `UserActivity`: Track user actions (posts, replies, likes, bookmarks)
- `UserStats`: Aggregated metrics and rankings
- `UserBookmark`: Save references for forums and use cases
- `DraftPost`: Complete draft persistence separate from published content
- `Invitation`: Email invitations with 7-day token expiry

### 5. Service Layer (`app/services/`)

| Service | Responsibility |
|---------|---------------|
| `UserService` | User creation with dual-database support |
| `ForumService` | Forum CRUD, replies, likes, view tracking |
| `UseCaseService` | Use case management, slug generation, organization linking |
| `InvitationService` | Token generation, validation, email sending |
| `UserActivityService` | Activity logging, stats calculation |
| `S3Service` | File upload/download with multi-bucket support |
| `EmailService` | SMTP email sending with HTML templates |
| `EmailVerificationService` | Verification email with production URLs |

### 6. Security Features

- SuperTokens session validation on all protected endpoints
- User ownership verification for content edit/delete
- File type validation with magic byte checking
- Size limit enforcement (5MB images, 50MB videos)
- Email verification required for admin signups
- Soft deletes preserve audit trails
- S3 bucket access restricted to authenticated users
- CORS properly configured for cross-origin requests

---

## Special Implementation Details

### Draft System (Story 12)
- Separate `DraftPost` collection from published `ForumPost`
- Auto-save to localStorage + backend persistence
- Ability to "continue writing" drafts
- Forum post creation with draft pre-fill

### Smart Point System (Story 6)
- 50 points per forum post created
- 20 points per reply
- 5 points per like received
- 30 bonus points for best answer
- Real-time contributor ranking

### Dynamic Category System (Story 11)
- 35+ predefined manufacturing categories
- Real-time category refresh on post creation/deletion
- Case-insensitive normalization
- MongoDB aggregation pipeline for efficiency

### Invitation & Organization System (Story 15)
- Email invitations with 7-day token expiry
- Auto-organization creation based on email domain
- Organization inheritance for invited members
- Role assignment: invites = "member", self-signup = "admin"
- Test mode: redirects all invitations to `hamzaferoze115@gmail.com`

### Media Upload System (Story 17)
- AWS S3 integration with multi-bucket architecture
- Profile pictures: 5MB limit
- Forum attachments: 5MB images, 50MB videos
- Use case media: Multiple files with batch upload
- CloudFront CDN for global delivery
- Automatic cleanup on deletion
- PostgreSQL tracking + MongoDB synchronization

### Comprehensive Use Case Seeding (Story 16)
- 19 pre-built use cases from 6 team members
- Standardized factory name: "KACST Industry 4.0 Capability Center"
- Standardized vendor: "IIoT Solutions (with KACST)"
- Individual seed scripts for each team member
- JSON data files with real technical details
- Migration scripts for data structure fixes

---

## Critical Fixes & Migrations Documented

### Authorization Issues (Story 18)
- MongoDB ObjectId used as stable user identifier
- SuperTokens IDs can change — not suitable for ownership checks
- Email-based fallback for cross-session authorization

### Field Mapping Issues (Story 18)
- `subtitle` and `executive_summary` were missing from creation
- `city` field saved as `region` instead of `city`
- Architecture components schema mismatches
- Migration script (`migrate_usecase_fields_complete.py`) for existing data

### Data Synchronization (Story 17)
- Media metadata stored in PostgreSQL (`user_media` table)
- Media references stored in MongoDB (`ForumPost.attachments`, `UseCase.images`)
- Automatic sync on upload, manual migration for legacy data

### Production URL Fixes (Stories 15, 17, 20)
- Hardcoded production IP in invitation/verification emails
- Ensures links work regardless of deployment environment
- Console logs contain localhost versions for development

---

## S3 Bucket Configuration

**3 S3 Buckets documented**:
1. **Profile Pictures Bucket**: User avatars, 5MB max
2. **Forum Attachments Bucket**: Forum media, 5MB images / 50MB videos
3. **Use Case Media Bucket**: Case study images and documents

**AWS Region**: `me-south-1` (Middle East - Bahrain)
**CDN**: CloudFront distribution for global delivery

---

## Use Case Fields Documentation

Comprehensive field-by-field specification for the UseCase model:
- 9 main sections in the submission form
- 50+ individual fields documented
- Validation rules for each field
- Required vs optional field designation
- Data types and constraints

---

## Testing & Seeding

**Seed Data Scripts** (`p2p-backend-app/scripts/`):
| Script | Purpose |
|--------|---------|
| `seed_db_users.py` | 18 demo users with diverse roles |
| `seed_forums.py` | Forum posts across categories |
| `seed_usecases.py` | 15 base use cases |
| `seed_user_activities.py` | User engagement metrics |
| `seed_[name].py` | 6 individual team member seeding scripts |
| `verify_existing_users.py` | Mark legacy users as email-verified |
| `remove_usecases.py` | Clean removal of seeded content |
| `seed_all.py` | Master seeder that runs everything |

**Testing Credentials**:
- Admin: `aadil@iiotsolutions.sa` / `password123`
- Demo users: `user1@example.com` through `user18@example.com` / `password123`
- All seeded users fully email-verified

---

## Known Issues & Gotchas

1. **WSL2 Performance**: Git operations slow on `/mnt/c/` — use native PowerShell
2. **Docker Context**: Must navigate to `docker/` directory before compose commands
3. **SuperTokens Database**: Requires separate dedicated database, not shared with application
4. **CORS Configuration**: SuperTokens middleware must come BEFORE CORS middleware
5. **Field Name Inconsistencies**: Frontend/backend sometimes use different names (camelCase vs snake_case)
6. **Database Race Conditions**: Proper health checks and retry logic required

---
project: P2P-V2
created: 2025-12-31T15:30:00
last_updated: 2025-12-31T15:30:00
last_commit: e808252
update_count: 1
total_files: 252
total_folders: 40
---

# Project Map: P2P Manufacturing Knowledge Platform

## Overview

The P2P (Peer-to-Peer) Manufacturing Knowledge Platform is a comprehensive web application designed to connect manufacturers in Saudi Arabia, facilitate knowledge sharing, and enable collaborative problem-solving in the manufacturing industry. The platform enables verified users—factory owners, plant engineers, and operations managers—to share insights, solve problems through forums, and access Industry 4.0 case studies within a trusted, community-driven environment.

The application follows a three-tier architecture with a React frontend, FastAPI backend, and a dual-database system using PostgreSQL for core user data and MongoDB for rich content like forum posts, use cases, and user profiles. Authentication is handled through SuperTokens with email/password authentication and email verification. The platform features an interactive map showing use case locations across Saudi Arabia, a forum system with replies and best answers, and a comprehensive use case submission wizard.

The project is fully containerized with Docker, supporting both development and production deployments. It includes database seeding scripts for demo data, Alembic migrations for PostgreSQL schema management, and AWS S3 integration for media uploads including profile pictures and use case attachments.

## Tech Stack

**Languages:** Python 3.11, TypeScript, JavaScript
**Frameworks:** FastAPI, React 18, Vite 7
**Tools:** Docker, Tailwind CSS 4, Alembic, Beanie ODM
**Databases:** PostgreSQL 16, MongoDB 7, SuperTokens
**Cloud:** AWS S3 (media storage), AWS EC2 (hosting)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │     React 18 + Vite + TypeScript + Tailwind CSS + Leaflet Maps     ││
│  │         SuperTokens Auth React SDK  |  React Router                 ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                    FastAPI + Uvicorn                                ││
│  │  ┌───────────┬───────────┬───────────┬───────────┬───────────────┐ ││
│  │  │   Auth    │  Forum    │ Use Cases │  Media    │   Dashboard   │ ││
│  │  │ Endpoints │ Endpoints │ Endpoints │ Endpoints │   Endpoints   │ ││
│  │  └───────────┴───────────┴───────────┴───────────┴───────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  SuperTokens    │  │   PostgreSQL    │  │    MongoDB      │
│  (Auth Core)    │  │  (Core Users,   │  │  (Profiles,     │
│                 │  │   Sessions)     │  │   Forums,       │
│                 │  │                 │  │   Use Cases)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────┐
                                         │    AWS S3       │
                                         │  (Media Files)  │
                                         └─────────────────┘
```

## Directory Structure

### 📂 p2p-backend-app/

**Purpose:** Python FastAPI backend application containing all API endpoints, services, and database models.

**What it does:**
- Provides RESTful API endpoints for authentication, forums, use cases, and media uploads
- Manages dual-database architecture with PostgreSQL and MongoDB
- Handles SuperTokens authentication integration
- Processes file uploads to AWS S3

**Contains:** app/, alembic/, scripts/

---

#### 📂 p2p-backend-app/app/

**Purpose:** Main application source code directory containing the FastAPI application structure.

**What it does:**
- Houses the FastAPI app initialization and configuration
- Contains all API routes organized by version
- Stores database models for both PostgreSQL and MongoDB
- Implements business logic services

**Contains:** api/, core/, models/, schemas/, services/

---

#### 🐍 main.py

**Path:** `p2p-backend-app/app/main.py`

**Purpose:** FastAPI application entry point and configuration.

**What it does:**
- Initializes the FastAPI application with lifespan management
- Configures CORS middleware with SuperTokens headers
- Sets up SuperTokens authentication middleware
- Manages database connections on startup/shutdown

**Key Functions:**
- `lifespan()` — Async context manager for startup/shutdown events
- `root()` — Root endpoint returning API info

**Integrates with:** → `core/config.py`, → `core/database.py`, → `core/supertokens.py`, → `api/v1/api.py`

---

#### 📂 p2p-backend-app/app/core/

**Purpose:** Core application configuration and infrastructure modules.

**What it does:**
- Manages application settings and environment variables
- Handles database connections with retry logic
- Configures SuperTokens authentication
- Sets up logging infrastructure

---

#### 🐍 config.py

**Path:** `p2p-backend-app/app/core/config.py`

**Purpose:** Application settings and environment configuration using Pydantic.

**What it does:**
- Defines all application settings with defaults
- Loads configuration from environment variables and .env file
- Configures CORS origins, database URLs, and AWS credentials
- Manages SuperTokens and email service settings

**Key Classes:**
- `Settings` — Pydantic BaseSettings class with all configuration options

**Integrates with:** → All modules that need configuration

---

#### 🐍 database.py

**Path:** `p2p-backend-app/app/core/database.py`

**Purpose:** Database connection management for PostgreSQL and MongoDB.

**What it does:**
- Initializes async SQLAlchemy engine for PostgreSQL
- Sets up Motor async client for MongoDB with Beanie ODM
- Implements connection retry logic with exponential backoff
- Provides dependency injection for database sessions

**Key Functions:**
- `init_postgres()` — Initialize PostgreSQL with connection pooling
- `init_mongodb()` — Initialize MongoDB and Beanie document models
- `get_db()` — Async generator for PostgreSQL session dependency

**Key Classes:**
- `DatabaseManager` — Singleton managing all database connections

**Integrates with:** → `models/pg_models.py`, → `models/mongo_models.py`

---

#### 🐍 supertokens.py

**Path:** `p2p-backend-app/app/core/supertokens.py`

**Purpose:** SuperTokens authentication initialization and email delivery customization.

**What it does:**
- Initializes SuperTokens with email/password recipe
- Configures email verification as required mode
- Customizes email delivery for verification and password reset
- Sets up session management with cookie configuration

**Key Functions:**
- `init_supertokens()` — Main initialization function
- `custom_email_delivery_override()` — Custom verification email sender
- `custom_password_reset_email_override()` — Custom password reset email sender

**Integrates with:** → `services/email_verification_service.py`, → `services/password_reset_service.py`

---

#### 📂 p2p-backend-app/app/api/v1/

**Purpose:** API version 1 route definitions and endpoint implementations.

**What it does:**
- Organizes all API endpoints by feature domain
- Provides the main API router that aggregates all sub-routers
- Implements authentication, forum, use case, and media endpoints

---

#### 🐍 api.py

**Path:** `p2p-backend-app/app/api/v1/api.py`

**Purpose:** Main API router that aggregates all endpoint routers.

**What it does:**
- Creates the main APIRouter instance
- Includes all feature routers with appropriate prefixes
- Organizes endpoints into tagged groups for OpenAPI docs

**Integrates with:** → `endpoints/auth.py`, → `endpoints/supertokens_auth.py`, → `endpoints/forum.py`, → `endpoints/usecases.py`, → `endpoints/media.py`, → `endpoints/dashboard.py`, → `endpoints/invites.py`

---

#### 📂 p2p-backend-app/app/api/v1/endpoints/

**Purpose:** Individual API endpoint implementations organized by feature.

---

#### 🐍 supertokens_auth.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py`

**Purpose:** Custom authentication endpoints for signup, signin, and password management.

**What it does:**
- Implements custom signup flow creating users in SuperTokens and both databases
- Handles member invitation validation during signup
- Manages email verification token creation and verification
- Provides password reset functionality

**Key Functions:**
- `post_signup()` — Custom signup creating user across all systems
- `post_signin()` — Custom signin with session creation
- `send_verification_email()` — Triggers verification email
- `reset_password()` — Handles password reset flow

**Integrates with:** → `services/database_service.py`, → `models/mongo_models.py`

---

#### 🐍 auth.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/auth.py`

**Purpose:** User profile management and session information endpoints.

**What it does:**
- Provides current user profile endpoint (/me)
- Handles profile updates including profile picture
- Manages organization member listing
- Implements user deletion with cascade cleanup

**Integrates with:** → `services/database_service.py`, → `services/s3_service.py`

---

#### 🐍 forum.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/forum.py`

**Purpose:** Forum post and reply management endpoints.

**What it does:**
- Creates, reads, updates, and deletes forum posts
- Manages replies with nested threading support
- Handles post/reply likes and best answer marking
- Supports draft post functionality
- Processes media attachments for posts and replies

**Integrates with:** → `services/forum_service.py`, → `models/mongo_models.py`

---

#### 🐍 usecases.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/usecases.py`

**Purpose:** Use case submission and management endpoints.

**What it does:**
- Creates comprehensive use cases with multi-step wizard data
- Retrieves use cases with filtering by region, category, and tags
- Manages use case drafts with autosave functionality
- Handles use case media uploads and bookmarking
- Provides slug-based URL routing for SEO-friendly URLs

**Integrates with:** → `services/usecase_service.py`, → `models/mongo_models.py`, → `services/s3_service.py`

---

#### 🐍 media.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/media.py`

**Purpose:** Media file upload and management endpoints.

**What it does:**
- Handles profile picture uploads with image validation
- Manages forum and use case media attachments
- Generates presigned URLs for direct S3 uploads
- Tracks uploaded files in PostgreSQL for user association

**Integrates with:** → `services/s3_service.py`, → `models/pg_models.py`

---

#### 🐍 dashboard.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/dashboard.py`

**Purpose:** Dashboard analytics and activity feed endpoints.

**What it does:**
- Provides platform statistics (users, posts, use cases)
- Returns recent forum activity feed
- Calculates user engagement metrics
- Aggregates trending topics and categories

**Integrates with:** → `services/user_activity_service.py`, → `models/mongo_models.py`

---

#### 🐍 invites.py

**Path:** `p2p-backend-app/app/api/v1/endpoints/invites.py`

**Purpose:** Organization member invitation management.

**What it does:**
- Creates invitation tokens for new members
- Sends invitation emails with signup links
- Validates invitation tokens during signup
- Lists pending and used invitations for admins

**Integrates with:** → `services/invitation_service.py`, → `services/email_service.py`

---

#### 📂 p2p-backend-app/app/models/

**Purpose:** Database model definitions for PostgreSQL and MongoDB.

---

#### 🐍 pg_models.py

**Path:** `p2p-backend-app/app/models/pg_models.py`

**Purpose:** SQLAlchemy models for PostgreSQL core data.

**What it does:**
- Defines User model linked to SuperTokens via supertokens_id
- Manages user sessions and media file tracking
- Provides system configuration storage

**Key Classes:**
- `User` — Core user with email, name, role, profile picture URL
- `UserSession` — Session tracking for analytics
- `UserMedia` — S3 file tracking with user association
- `SystemConfig` — Key-value configuration storage

---

#### 🐍 mongo_models.py

**Path:** `p2p-backend-app/app/models/mongo_models.py`

**Purpose:** Beanie document models for MongoDB rich content.

**What it does:**
- Defines extended user profiles with organization linkage
- Models forum posts with attachments, likes, and best answers
- Stores comprehensive use case data with location coordinates
- Tracks user activities, stats, and bookmarks

**Key Classes:**
- `User` — Extended profile with expertise tags, company info
- `Organization` — Company/organization data with domain
- `ForumPost` — Forum posts with replies, likes, attachments
- `ForumReply` — Nested replies with best answer support
- `UseCase` — Comprehensive use case with rich sections
- `UseCaseDraft` — Partial use case saves during wizard
- `UserActivity` — Activity feed events
- `UserStats` — Aggregated user statistics
- `Invitation` — Member invitation tokens

---

#### 📂 p2p-backend-app/app/services/

**Purpose:** Business logic services implementing core functionality.

---

#### 🐍 database_service.py

**Path:** `p2p-backend-app/app/services/database_service.py`

**Purpose:** User and content management service layer.

**What it does:**
- Creates users in both PostgreSQL and MongoDB atomically
- Manages organization creation/linking by email domain
- Enforces single admin per organization rule
- Provides forum and use case CRUD operations

**Key Classes:**
- `UserService` — Dual-database user management
- `ForumService` — Forum post and reply operations
- `UseCaseService` — Use case creation and retrieval

---

#### 🐍 s3_service.py

**Path:** `p2p-backend-app/app/services/s3_service.py`

**Purpose:** AWS S3 file upload and management service.

**What it does:**
- Uploads files to appropriate S3 buckets by type
- Generates unique S3 keys with timestamps
- Creates presigned URLs for direct uploads
- Validates file types and sizes

**Key Functions:**
- `upload_file()` — Upload file to S3 bucket
- `generate_presigned_url()` — Create direct upload URL
- `delete_file()` — Remove file from S3

---

#### 🐍 email_service.py

**Path:** `p2p-backend-app/app/services/email_service.py`

**Purpose:** Email sending service using SMTP.

**What it does:**
- Sends HTML emails for verification and invitations
- Supports password reset email templates
- Handles SMTP connection with TLS

---

#### 📂 p2p-backend-app/scripts/

**Purpose:** Database seeding and utility scripts for development and demos.

**What it does:**
- Seeds demo users and team members
- Populates use cases and forum posts
- Verifies existing users for testing
- Migrates use case field structures

---

#### 🐍 seed_all.py

**Path:** `p2p-backend-app/scripts/seed_all.py`

**Purpose:** Master seeding script that runs all seed operations.

**What it does:**
- Orchestrates complete demo data seeding
- Seeds 24 users, 34 use cases, forums, and activities
- Verifies all users for immediate login access

---

#### 📂 p2p-backend-app/alembic/

**Purpose:** PostgreSQL database migration management.

**What it does:**
- Tracks schema changes with versioned migrations
- Handles initial table creation and modifications
- Supports profile picture and media table additions

---

### 📂 p2p-frontend-app/

**Purpose:** React TypeScript frontend application with Vite build tooling.

**What it does:**
- Provides the user interface for the P2P platform
- Implements authentication flows with SuperTokens
- Renders interactive Saudi Arabia map with use cases
- Manages forum discussions and use case submissions

**Contains:** src/, public/

---

#### 📂 p2p-frontend-app/src/

**Purpose:** Frontend source code including components, pages, and configuration.

---

#### 🟦 App.tsx

**Path:** `p2p-frontend-app/src/App.tsx`

**Purpose:** Main React application component with routing configuration.

**What it does:**
- Sets up React Router with all application routes
- Wraps app in AuthProvider for authentication state
- Configures protected routes requiring authentication
- Renders Navigation and MobileBottomNav components

**Key Components:**
- Public routes: LandingPage, Login, Signup, MemberSignup, ForgotPassword
- Protected routes: Dashboard, Forum, UseCases, SubmitUseCase, UserManagement

**Integrates with:** → `contexts/AuthContext.tsx`, → `components/Navigation.tsx`, → `pages/*`

---

#### 🟦 main.tsx

**Path:** `p2p-frontend-app/src/main.tsx`

**Purpose:** Application entry point rendering root component.

**What it does:**
- Initializes React DOM rendering
- Wraps app in SuperTokensWrapper for auth SDK
- Imports global CSS and SuperTokens configuration

**Integrates with:** → `App.tsx`, → `config/supertokens.ts`

---

#### 📂 p2p-frontend-app/src/config/

**Purpose:** Application configuration modules.

---

#### 🟦 environment.ts

**Path:** `p2p-frontend-app/src/config/environment.ts`

**Purpose:** Smart environment detection and API URL configuration.

**What it does:**
- Detects production vs development based on hostname
- Provides API_BASE_URL and WEBSITE_BASE_URL exports
- Offers helper functions for building URLs

**Key Functions:**
- `buildApiUrl()` — Constructs full API endpoint URLs
- `buildWebsiteUrl()` — Constructs full website URLs

---

#### 🟦 supertokens.ts

**Path:** `p2p-frontend-app/src/config/supertokens.ts`

**Purpose:** SuperTokens frontend SDK initialization.

**What it does:**
- Configures SuperTokens with app info and recipes
- Sets up EmailPassword and EmailVerification recipes
- Initializes Session recipe for auth state

---

#### 📂 p2p-frontend-app/src/contexts/

**Purpose:** React context providers for global state management.

---

#### 🟦 AuthContext.tsx

**Path:** `p2p-frontend-app/src/contexts/AuthContext.tsx`

**Purpose:** Authentication state management context.

**What it does:**
- Manages user authentication state globally
- Provides login, signup, and logout functions
- Fetches and caches user profile from API
- Handles session checking on app load

**Key Functions:**
- `login()` — Authenticates user and fetches profile
- `signup()` — Creates account and handles email verification
- `logout()` — Clears session and auth state
- `refreshProfile()` — Re-fetches user profile

---

#### 📂 p2p-frontend-app/src/components/

**Purpose:** Reusable React components.

---

#### 🟦 Navigation.tsx

**Path:** `p2p-frontend-app/src/components/Navigation.tsx`

**Purpose:** Main navigation header and mobile bottom nav.

**What it does:**
- Renders responsive navigation with desktop and mobile variants
- Shows user avatar and profile dropdown when authenticated
- Provides edit profile slide-over panel
- Handles logout and navigation actions

---

#### 🟦 InteractiveMap.tsx

**Path:** `p2p-frontend-app/src/components/InteractiveMap.tsx`

**Purpose:** Leaflet-based interactive map of Saudi Arabia showing use cases.

**What it does:**
- Renders map with OpenStreetMap tiles
- Displays use case markers with clustering
- Shows popup cards with use case details
- Handles marker click navigation to use case detail

---

#### 🟦 EditProfilePanel.tsx

**Path:** `p2p-frontend-app/src/components/EditProfilePanel.tsx`

**Purpose:** Slide-over panel for editing user profile.

**What it does:**
- Provides form for updating profile information
- Handles profile picture upload with preview
- Manages account settings like password change

---

#### 📂 p2p-frontend-app/src/components/ui/

**Purpose:** UI primitive components based on shadcn/ui patterns.

**What it does:**
- Provides Button, Card, Input, Select, Dialog components
- Implements form components with React Hook Form integration
- Contains custom components like FileDropZone, MediaGallery

---

#### 📂 p2p-frontend-app/src/pages/

**Purpose:** Page-level components for each route.

---

#### 🟦 LandingPage.tsx

**Path:** `p2p-frontend-app/src/pages/LandingPage.tsx`

**Purpose:** Public landing page with platform overview.

**What it does:**
- Displays hero section with call-to-action
- Shows interactive map with featured use cases
- Presents platform features and benefits

---

#### 🟦 Dashboard.tsx

**Path:** `p2p-frontend-app/src/pages/Dashboard.tsx`

**Purpose:** User dashboard with activity feed and stats.

**What it does:**
- Shows user's recent activity and contributions
- Displays platform statistics and metrics
- Provides quick access to common actions

---

#### 🟦 Forum.tsx

**Path:** `p2p-frontend-app/src/pages/Forum.tsx`

**Purpose:** Forum discussion board with posts and replies.

**What it does:**
- Lists forum posts with filtering by category
- Supports post creation with rich text and attachments
- Manages replies with nested threading
- Handles likes and best answer marking

---

#### 🟦 UseCases.tsx

**Path:** `p2p-frontend-app/src/pages/UseCases.tsx`

**Purpose:** Use case library listing page.

**What it does:**
- Displays use case cards with filtering options
- Provides search by title, category, and tags
- Shows use case locations on map view

---

#### 🟦 SubmitUseCase.tsx

**Path:** `p2p-frontend-app/src/pages/SubmitUseCase.tsx`

**Purpose:** Multi-step wizard for submitting new use cases.

**What it does:**
- Guides users through 7-step submission process
- Handles autosave of drafts to server
- Manages media uploads for images and videos
- Validates required fields at each step

---

#### 🟦 UseCaseDetail.tsx

**Path:** `p2p-frontend-app/src/pages/UseCaseDetail.tsx`

**Purpose:** Detailed view of a single use case.

**What it does:**
- Displays all use case sections and media
- Shows implementation phases and results
- Provides bookmark and share functionality

---

#### 🟦 Login.tsx

**Path:** `p2p-frontend-app/src/pages/Login.tsx`

**Purpose:** User login page.

**What it does:**
- Provides email/password login form
- Handles authentication errors
- Links to signup and password reset

---

#### 🟦 Signup.tsx

**Path:** `p2p-frontend-app/src/pages/Signup.tsx`

**Purpose:** Admin/organization signup page.

**What it does:**
- Collects organization and personal information
- Creates admin user with new organization
- Triggers email verification for admins

---

#### 🟦 MemberSignup.tsx

**Path:** `p2p-frontend-app/src/pages/MemberSignup.tsx`

**Purpose:** Invited member signup page.

**What it does:**
- Validates invitation token from URL
- Creates member user in inviter's organization
- Auto-verifies email for invited users

---

#### 🟦 UserManagement.tsx

**Path:** `p2p-frontend-app/src/pages/UserManagement.tsx`

**Purpose:** Admin page for managing organization members.

**What it does:**
- Lists organization members
- Provides member invitation functionality
- Shows pending and used invitations

---

### 📂 docker/

**Purpose:** Docker configuration files for containerized deployment.

**What it does:**
- Defines development and production compose configurations
- Provides Dockerfiles for backend and frontend services
- Configures PostgreSQL, MongoDB, and SuperTokens containers

---

#### ⚙️ development_docker-compose.yml

**Path:** `docker/development_docker-compose.yml`

**Purpose:** Docker Compose configuration for local development.

**What it does:**
- Orchestrates all services with hot reload support
- Configures PostgreSQL 16, MongoDB 7, SuperTokens
- Sets up volume mounts for live code changes
- Defines health checks and service dependencies

---

#### ⚙️ docker-compose.yml

**Path:** `docker/docker-compose.yml`

**Purpose:** Docker Compose configuration for production deployment.

**What it does:**
- Builds optimized production images
- Configures production environment variables
- Uses nginx for frontend static serving

---

#### 🐳 backend.Dockerfile

**Path:** `docker/backend.Dockerfile`

**Purpose:** Multi-stage Dockerfile for Python FastAPI backend.

**What it does:**
- Defines development and production build stages
- Installs Python dependencies with pip
- Runs Uvicorn server with appropriate workers

---

#### 🐳 frontend.Dockerfile

**Path:** `docker/frontend.Dockerfile`

**Purpose:** Multi-stage Dockerfile for React frontend.

**What it does:**
- Defines development stage with Vite dev server
- Builds production assets with npm
- Uses nginx for production static file serving

---

#### 📄 init-db.sql

**Path:** `docker/init-db.sql`

**Purpose:** PostgreSQL initialization script.

**What it does:**
- Creates the supertokens database for auth service
- Runs automatically on first container start

---

### 📂 backend docs/

**Purpose:** Implementation documentation for completed development stories.

**What it does:**
- Documents each story's implementation details
- Records architecture decisions and changes
- Provides troubleshooting guides

---

### 📂 docs/

**Purpose:** Project documentation including PRD, architecture, and user stories.

**What it does:**
- Contains product requirements document
- Defines system architecture
- Organizes user stories by epic

---

## Git History

**Branch:** hamza-backend
**Last Commit:** e808252
**Total Commits:** 63
**Repository:** Local

### Recent Commits

#### 🔵 e808252 — Fix critical security vulnerabilities and improve password reset flow
**Author:** Hamza Feroze
**Date:** December 07, 2025
- Security improvements to password reset flow
- Enhanced error message sanitization

#### 🔵 a7aa78d — Implement email verification resend functionality with custom email service
**Author:** Hamza Feroze
**Date:** November 13, 2025
- Added resend verification email endpoint
- Integrated custom email service for verification

#### 🔵 2a692a9 — Fix TypeScript compilation errors in ResetPassword and SubmitUseCase
**Author:** Hamza Feroze
**Date:** November 10, 2025
- Fixed TypeScript errors across frontend components
- Improved type safety in form handling

#### 🔵 3af39b5 — Fix responsive navigation breakpoints to prevent UI crowding on medium screens
**Author:** Hamza Feroze
**Date:** November 10, 2025
- Adjusted navigation breakpoints for better responsiveness
- Fixed mobile menu behavior

#### 🔵 630b374 — Add to gitignore
**Author:** Hamza Feroze
**Date:** November 09, 2025
- Updated gitignore with new patterns

#### 🔵 cc48165 — Implement complete draft system with autosave, server storage, and "Start New Use Case" feature
**Author:** Hamza Feroze
**Date:** November 09, 2025
- Added UseCaseDraft model for server-side draft storage
- Implemented autosave functionality in SubmitUseCase wizard
- Added ability to start fresh use case while preserving draft

#### 🔵 5a9a764 — Fix login image import to use Vite asset handling
**Author:** Hamza Feroze
**Date:** October 29, 2025
- Fixed asset import for login page background

#### 🔵 64a591e — Implement single admin per organization restriction and login UI improvements
**Author:** Hamza Feroze
**Date:** October 29, 2025
- Enforced one admin per organization domain
- Improved login page UI design

#### 🔵 d8e7cfc — Fix TypeScript compilation errors across frontend components
**Author:** Hamza Feroze
**Date:** October 23, 2025
- Resolved type errors in multiple components

#### 🔵 eda5d9f — Switch S3 buckets from development to production
**Author:** Hamza Feroze
**Date:** October 23, 2025
- Updated S3 bucket configuration for production

### Top Contributors

1. Hamza Feroze (63 commits)

## Update History

### December 31, 2025 (Latest)

Initial project map created with 252 files across 40 folders.

**Documented:**
- Complete backend API structure with 9 endpoint modules
- Frontend React application with 16 pages
- Docker containerization setup
- Database models for PostgreSQL and MongoDB
- Service layer implementations
- Authentication flow with SuperTokens

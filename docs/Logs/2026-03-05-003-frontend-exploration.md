# Frontend Application Exploration Log

**Date:** 2026-03-05
**Session:** 003
**Agent:** Frontend Explorer

## Objective

Comprehensive exploration of the `p2p-frontend-app/` directory — every component, page, context, config, type definition, routing structure, and architectural pattern.

## Summary

The frontend is a React 18/19 + TypeScript application built with Vite, totaling ~13,475 lines of code across 51 TSX files. It uses Tailwind CSS 4.1 with Radix UI components, SuperTokens for authentication, Leaflet for interactive maps, React Hook Form + Zod for form handling, and React Router DOM v7 for routing. It features 14 pages, 23 components, and 17 UI components.

---

## Directory Structure

```
p2p-frontend-app/
├── src/
│   ├── main.tsx                          # React entry point with SuperTokens wrapper
│   ├── App.tsx                           # Main routing config, protected routes, layout
│   ├── index.css                         # Global styles
│   ├── vite-env.d.ts                     # Vite environment type definitions
│   │
│   ├── components/
│   │   ├── Navigation.tsx                # Fixed header + mobile bottom nav
│   │   ├── ProtectedRoute.tsx            # Auth gate component
│   │   ├── ScrollToTop.tsx               # Route change scroll behavior
│   │   ├── EditProfilePanel.tsx          # Profile/password/email update modal
│   │   ├── InteractiveMap.tsx            # Leaflet map with use case markers/clustering
│   │   ├── LocationPicker.tsx            # Location selection for use cases
│   │   ├── UseCasePopup.tsx              # Map popup generator
│   │   ├── SaudiRiyal.tsx                # Currency formatter component
│   │   ├── SaudiRiyalTest.tsx            # Currency testing component
│   │   ├── ImageUpload.tsx               # Legacy image upload
│   │   ├── Auth/                         # (Directory exists but empty)
│   │   │
│   │   └── ui/                           # Headless UI components (Radix-based)
│   │       ├── button.tsx                # Variant-based button
│   │       ├── input.tsx                 # Input field
│   │       ├── textarea.tsx              # Text area
│   │       ├── label.tsx                 # Form label
│   │       ├── select.tsx                # Select dropdown
│   │       ├── dialog.tsx                # Modal dialog
│   │       ├── card.tsx                  # Card wrapper
│   │       ├── form.tsx                  # React Hook Form integration
│   │       ├── navigation-menu.tsx       # Radix navigation menu
│   │       ├── Avatar.tsx                # User avatar with initials fallback
│   │       ├── CreatePostModal.tsx       # Forum post creation with drafts
│   │       ├── DeleteConfirmModal.tsx    # Confirmation dialog
│   │       ├── ComingSoonModal.tsx       # Placeholder for future features
│   │       ├── FileDropZone.tsx          # Drag-drop file upload
│   │       ├── ImageUploader.tsx         # File preview + upload
│   │       ├── ProfilePictureEditor.tsx  # Avatar cropper
│   │       └── MediaGallery.tsx          # Image/video gallery display
│   │
│   ├── pages/
│   │   ├── LandingPage.tsx               # Home hero + features + stats
│   │   ├── Login.tsx                     # Email/password login
│   │   ├── Signup.tsx                    # Multi-step admin registration
│   │   ├── MemberSignup.tsx              # Invited member registration
│   │   ├── ForgotPassword.tsx            # Password reset request
│   │   ├── ResetPassword.tsx             # Password reset form
│   │   ├── EmailVerificationPending.tsx  # Verification status check
│   │   ├── EmailVerificationSuccess.tsx  # Verification completion
│   │   ├── Dashboard.tsx                 # User stats, activities, drafts, bookmarks
│   │   ├── Forum.tsx                     # Discussion board with categories
│   │   ├── UseCases.tsx                  # Browsable use case gallery
│   │   ├── UseCaseDetail.tsx             # Detailed use case view
│   │   ├── SubmitUseCase.tsx             # Multi-section form (Zod validated)
│   │   ├── UserManagement.tsx            # Org admin: invite members
│   │   └── Connect.tsx                   # Member networking (coming soon)
│   │
│   ├── contexts/
│   │   └── AuthContext.tsx               # Auth state + signup/login/logout logic
│   │
│   ├── config/
│   │   ├── environment.ts                # API/website URL detection (smart hostname)
│   │   └── supertokens.ts                # SuperTokens SDK initialization
│   │
│   ├── types/
│   │   └── auth.ts                       # User, Organization, AuthState types
│   │
│   ├── lib/
│   │   └── utils.ts                      # cn() for Tailwind class merging
│   │
│   ├── data/
│   │   └── use-cases.json                # Mock use case data
│   │
│   └── assets/
│       ├── LOGIN.png                     # Login page background
│       └── react.svg                     # React logo
│
├── public/
│   ├── logo.png                          # PeerLink logo
│   ├── vite.svg                          # Vite logo
│   └── Video_Redo_Realistic_Technology.mp4  # Hero section background video
│
├── index.html                            # HTML entry point
├── package.json                          # Dependencies and scripts
├── vite.config.ts                        # Vite configuration
├── tsconfig.json                         # TypeScript config
├── tsconfig.app.json                     # App-specific TS config
├── tsconfig.node.json                    # Node-specific TS config
├── eslint.config.js                      # Linting rules
├── tailwind.config.js                    # Tailwind customization
└── components.json                       # Radix UI component registry
```

---

## Configuration Files

### `vite.config.ts`
- React plugin for JSX transformation
- Tailwind CSS Vite plugin
- Path alias: `@` → `./src`
- Dev server: port 5173 with polling (for Docker volume mounts)
- Build targets: ES2015 (production), ESNext (development)

### `package.json` — Key Dependencies

**Frontend Core**:
| Package | Version | Purpose |
|---------|---------|---------|
| react | 19.1.0 | Core framework |
| react-dom | 19.1.0 | DOM rendering |
| react-router-dom | 7.7.1 | Client-side routing |
| react-hook-form | 7.61.1 | Form state management |
| zod | 4.0.10 | Schema validation |

**UI & Styling**:
| Package | Version | Purpose |
|---------|---------|---------|
| @tailwindcss/vite | 4.1.11 | Tailwind CSS engine |
| @radix-ui/* | various | Headless UI components |
| lucide-react | 0.526.0 | Icon library |
| class-variance-authority | 0.7.1 | CSS class variants |

**Authentication**:
| Package | Version | Purpose |
|---------|---------|---------|
| supertokens-auth-react | 0.49.1 | Frontend auth SDK |
| supertokens-web-js | 0.15.0 | Session management |

**Maps**:
| Package | Version | Purpose |
|---------|---------|---------|
| leaflet | 1.9.4 | Interactive maps |
| react-leaflet | 5.0.0 | React wrapper |
| leaflet.markercluster | 1.5.3 | Marker clustering |

### `tsconfig.json`
- Path mapping: `@/*` → `./src/*`
- Strict mode TypeScript

---

## Routing Architecture

### Public Routes (No Auth Required)

| Path | Component | Description |
|------|-----------|-------------|
| `/home` | LandingPage | Hero, features, stats |
| `/login` | Login | Email/password auth |
| `/signup` | Signup | Multi-step admin registration |
| `/join` | MemberSignup | Invitation-based registration |
| `/forgot-password` | ForgotPassword | Reset email request |
| `/reset-password?token=X` | ResetPassword | New password form |
| `/verify-email?email=X` | EmailVerificationPending | Status check |
| `/auth/verify-email?token=X` | EmailVerificationSuccess | Completion |

### Protected Routes (Auth Required)

| Path | Component | Description |
|------|-----------|-------------|
| `/dashboard` | Dashboard | Stats, activities, drafts, bookmarks |
| `/forum` | Forum | Discussion board with categories |
| `/usecases` | UseCases | Browsable gallery with filters |
| `/usecases/:company_slug/:title_slug` | UseCaseDetail | Detailed view |
| `/submit` | SubmitUseCase | Multi-section form |
| `/user-management` | UserManagement | Admin: invite members |
| `/connect` | Connect | Networking (coming soon) |

### Route Protection
- `ProtectedRoute` component checks `useAuth().isAuthenticated`
- Redirects to `/login` with location state if unauthenticated
- Shows loading spinner during session check

---

## Authentication & State Management

### AuthContext.tsx

**State**:
```typescript
AuthState {
  user: User | null
  organization: Organization | null
  isAuthenticated: boolean
  isLoading: boolean
}
```

**Methods**:
| Method | Description |
|--------|-------------|
| `login(credentials)` | POST to custom-signin, fetch profile, set state |
| `signup(data)` | POST to custom-signup, handle verification vs auto-login |
| `logout()` | Sign out SuperTokens session, clear state |
| `updateUser(user)` | Update local user state |
| `refreshProfile()` | Re-fetch profile from server |

**Session Persistence**:
- Checks `Session.doesSessionExist()` on mount
- Fetches `/api/v1/auth/me` with credentials
- Automatic refresh via SuperTokens SDK

### Data Fetching Pattern
```typescript
const [data, setData] = useState<T | null>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)

useEffect(() => {
  fetch(buildApiUrl('/api/v1/...'), { credentials: 'include' })
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err => setError(err.message))
    .finally(() => setLoading(false))
}, [deps])
```

---

## Page Components Deep Dive

### LandingPage.tsx
- Hero section with video background + dark overlay + CTA buttons
- Stats section: 1,200+ factories, 89 use cases, cost savings
- Features section
- Interactive map showing use case locations (Leaflet)
- Links to `/usecases` and `/forum`

### Login.tsx
- Email + password form with validation
- "Forgot Password" link, "Sign Up" redirect
- Error handling for email verification requirements
- Profile picture upload from localStorage (post-verification flow)
- Redirects to dashboard or previous location on success

### Signup.tsx (Multi-Step)
- **Step 1**: Personal info (name, email, password with validation: 8+ chars, lowercase + number)
- **Step 2**: Organization info (company, industry, size, city — Saudi cities list)
- **Step 3**: Profile picture (optional, with ProfilePictureEditor)
- Admin signup → requires email verification → stores profile pic in localStorage
- Invited member → auto-login → uploads profile pic immediately

### Dashboard.tsx
- **Stats Grid**: 9 metrics (questions, answers, bookmarks, reputation, use cases, best answers, activity level, connections, drafts)
- **Recent Activities Feed**: Type, user, action, timestamp
- **Bookmarks Modal**: Forum posts + use cases
- **Draft Posts Modal**: Unfinished forum drafts
- **Use Case Drafts Panel**: In-progress submissions
- Edit profile panel integration

### Forum.tsx
- **Sidebar**: Category list with post counts
- **Main area**: Post list with search and category filtering
- **Detail panel**: Full post + threaded comments with nested replies
- Like/bookmark functionality
- Edit/delete posts (own only)
- Media attachments support
- Top contributors leaderboard
- Post creation modal with draft saving

### UseCases.tsx
- Browse gallery with category filters
- Search by title/company
- Sort: newest, most popular, most saved
- Pagination (20 items/page)
- Like/save individual cases
- Top contributors section
- Links to detail pages via slugs

### SubmitUseCase.tsx (Zod Validated, 8 Sections)
1. **Basic Information**: Title, subtitle, description, category, factory name
2. **Location**: City dropdown (Saudi cities), map picker with lat/lng
3. **Business Challenge**: Industry context, specific problems (2-5), financial impact
4. **Solution Overview**: Selection criteria (2-5), vendor, technology components (1-15)
5. **Implementation Details**: Time, budget, methodology
6. **Results**: Quantitative metrics (2-4 with baseline/current/improvement), ROI %, savings
7. **Challenges & Solutions**: Challenge/solution/outcome entries (1-4)
8. **Contact & Media**: Contact person/title (optional), image uploads (max 5)

### UseCaseDetail.tsx
- Full content display from MongoDB
- Sections: Business challenge, solution details, implementation phases, results, ROI, challenges, technical architecture, future roadmap, lessons learned
- View count tracking, like/bookmark buttons, download, media gallery
- Edit/delete for author, share functionality

### UserManagement.tsx (Admin Only)
- Organization member list with search/filter by role
- Invite new members via email
- Pending invitations list
- Cancel pending invites

### Connect.tsx
- Coming Soon placeholder
- Intended: member directory, search, messaging, network visualization

---

## Key Components

### Navigation.tsx
- **Desktop (XL+)**: Logo + nav items (Home, Dashboard, Forum, Use Cases, Submit) + notification bell + avatar dropdown + logout
- **Tablet/Mobile**: Logo + hamburger menu + avatar
- **Mobile Bottom Nav**: 5-icon fixed bar (Home, Dashboard, Forum, Use Cases, Submit) — authenticated users only
- **Mobile Menu Overlay**: User info, profile edit, quick actions, login/logout

### EditProfilePanel.tsx
- **Profile Tab**: Name, title, location, expertise tags (add/remove), profile picture upload
- **Account Tab**: Email change form, password change form with visibility toggles

### InteractiveMap.tsx
- Leaflet with MarkerCluster for large datasets
- Dark CARTO tiles
- Custom marker icons with pulsing animation
- Zoom levels 5-20

### LocationPicker.tsx
- Draggable marker for lat/lng selection
- Used in SubmitUseCase form

### UI Components (Radix-Based)
| Component | Description |
|-----------|-------------|
| Avatar | Initials fallback, image loading, size variants |
| FileDropZone | Drag-drop with file type validation |
| ImageUploader | Preview before upload, size validation |
| MediaGallery | Image/video grid with lightbox |
| CreatePostModal | Forum post editor with draft support |
| DeleteConfirmModal | Confirmation dialog |
| ComingSoonModal | Future feature placeholder |
| ProfilePictureEditor | Avatar crop/upload |

---

## API Integration

### `buildApiUrl()` Helper (`config/environment.ts`)
```
Production: http://15.185.167.236:8000
Local: http://localhost:8000
Override: VITE_API_BASE_URL env var
```

Smart detection based on `window.location.hostname`.

### API Endpoints Used

**Auth**: `/api/v1/auth/custom-signup`, `/custom-signin`, `/me`, `/profile`, `/email`, `/password`, `/forgot-password`, `/reset-password`, `/resend-verification-email`

**Forum**: `/api/v1/forum/categories`, `/posts`, `/stats`, `/contributors`, `/bookmarks`

**Use Cases**: `/api/v1/use-cases` (list, detail, create, categories, stats, bookmarks, like)

**Media**: `/api/v1/media/profile-picture`, `/upload`

**Invitations**: `/api/v1/invites/send`, `/pending`, `/validate/:token`

**Dashboard**: `/api/v1/dashboard/stats`, `/activities`

---

## Type System (`types/auth.ts`)

### User
```typescript
{
  id: string, email: string
  firstName: string, lastName: string
  role: 'admin' | 'member'
  title: string, organizationId: string
  avatar?: string, profilePictureUrl?: string
  isActive: boolean, lastLogin?: Date, createdAt: Date
  company?: string, location?: string
  industrySector?: string, expertiseTags?: string[]
}
```

### Organization
```typescript
{
  id: string, name: string, domain: string
  industry: string
  size: 'startup' | 'small' | 'medium' | 'large' | 'enterprise'
  country: string, city: string
  logo?: string, isActive: boolean
  createdAt: Date, adminUserId: string
}
```

### SignupData
```typescript
{
  firstName: string, lastName: string
  email: string, password: string
  title: string
  organizationName: string, industry: string
  organizationSize: string, country: string, city: string
  inviteToken?: string, isInvited?: boolean
}
```

---

## Styling Architecture

- **Tailwind CSS 4.1** with Vite plugin
- **Responsive breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- **Common patterns**:
  - Gradient backgrounds: `bg-gradient-to-br from-slate-50 to-blue-50`
  - Shadows: `shadow-sm`, `shadow-lg`, `shadow-2xl`
  - Borders: slate-200 (light), blue-200 (interactive)
  - Rounded: `rounded-lg` default, `rounded-2xl` large
- **No dark mode** currently implemented
- **Mobile-first** responsive design

---

## Form Handling

- **React Hook Form** with Zod schema validation
- Dynamic field arrays for variable-length inputs
- Field-level error messages displayed inline
- Multi-step forms with progress indication
- File drop zones with preview before upload

---

## Data Flow Examples

### Login
```
User input → handleSubmit() → useAuth().login() →
POST /custom-signin → fetch /auth/me →
setAuthState({ user, org, isAuthenticated: true }) →
navigate to /dashboard
```

### Forum Post Creation
```
Fill form in CreatePostModal → select category + attachments →
POST /forum/posts (multipart) → backend stores in MongoDB →
success → onPostSuccess callback → modal closes → refetch posts
```

---

## File Statistics

| Category | Count | ~Lines |
|----------|-------|--------|
| Pages | 14 | ~3,500 |
| Components | 23 | ~4,200 |
| UI Components | 17 | ~2,800 |
| Config/Contexts | 3 | ~600 |
| Types | 1 | ~88 |
| Utils | 1 | ~6 |
| **TOTAL** | **51** | **~13,475** |

---

## Notable Implementation Details

### Profile Picture Handling
- **Admin signup**: Store in localStorage as base64 → upload after email verification on login
- **Invited member**: Upload immediately after signup
- **Profile edit**: ProfilePictureEditor with crop → POST to `/media/profile-picture`

### Map Integration
- Leaflet.markercluster for large datasets
- Dark CARTO tiles for clean visual style
- Custom marker icons with pulsing CSS animation
- Zoom levels 5-20, draggable marker for location picking

### Email Verification Flow
1. Admin signs up → receives verification email
2. Clicks link → `/auth/verify-email?token=X`
3. EmailVerificationSuccess page → verify button
4. POST `/auth/user/email/verify`
5. Success → redirect to `/login`
6. Login page handles pending profile picture upload from localStorage

---

## Missing / Future Work

- **No unit tests** (no Jest/Vitest configured)
- **No E2E tests** (no Cypress/Playwright)
- **No Storybook** for component documentation
- **No dark mode** support
- **No i18n/RTL** support (Arabic planned but not implemented)
- **Connect page**: Placeholder only (messaging, member directory planned)
- **No React Query/SWR** for data fetching (uses raw fetch + useState)
- **No virtual scrolling** for large lists
- **No request debouncing** on search inputs

---

## Security Considerations

**Implemented**:
- SuperTokens handles auth tokens and session refresh
- Credentials included in all API calls
- Zod schema validation on forms
- Password requirements enforced (8+ chars, lowercase, number)
- React auto-escaping prevents XSS

**Gaps**:
- No explicit CSRF tokens (handled by SuperTokens internally)
- No CSP headers visible
- File upload size limits in UI only (backend also enforces)

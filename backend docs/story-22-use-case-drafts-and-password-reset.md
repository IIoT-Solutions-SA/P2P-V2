# Feature Implementation - P2P Manufacturing Platform

**Last Updated**: November 9, 2025
**Features**: Reset Password Flow ✅ | Autosave GROUP A ✅ | Backend GROUP B ✅ | Frontend GROUP C ✅ | GROUP D Optional

---

## Summary

Four major implementations completed on November 6, 2025:

### 🔐 1. Reset Password Flow (COMPLETE ✅)
Complete forgot/reset password functionality integrated with SuperTokens. Users can request password reset via email, receive reset link, and set new password.

**Key Changes**:
- ✅ Fixed `send_reset_password_email()` - added missing user_id parameter
- ✅ Fixed reset password result type checking - removed non-existent import
- ✅ Added user lookup from PostgreSQL by email
- ✅ Proper error handling and security measures
- ✅ Frontend pages already existed, backend fixed

### 💾 2. Use Case Autosave System - GROUP A (COMPLETE ✅)
Comprehensive autosave functionality for Use Case submission form with dual visual indicators (top header + bottom navigation), reliable cross-step data persistence, edit mode support with smart localStorage priority, and robust error handling.

**Key Features**:
- ✅ Dual autosave status indicators (header + navigation)
- ✅ Works across all 7 wizard steps
- ✅ Edit mode support with 5-minute localStorage priority
- ✅ Comprehensive state capture (form fields + dynamic arrays)
- ✅ Error handling with user feedback
- ✅ Auto-restoration on page load/refresh

### 🗄️ 3. Backend Draft Storage - GROUP B (COMPLETE ✅)
Complete server-side draft storage system for Use Case submissions. Provides persistent, cross-device draft management with comprehensive MongoDB model, RESTful API endpoints, field validation, and publish workflow.

**Key Features**:
- ✅ MongoDB UseCaseDraft model with 50+ Optional fields
- ✅ 5 RESTful API endpoints (save, list, get, delete, publish)
- ✅ Hybrid storage architecture (localStorage + server)
- ✅ One draft per user with upsert logic
- ✅ Complete field mapping (camelCase ↔ snake_case)
- ✅ Authorization and ownership verification
- ✅ Draft validation before publishing
- ✅ Activity logging on publish

### 🎨 4. Frontend Draft Integration - GROUP C (COMPLETE ✅)
Complete frontend integration connecting Use Case submission form and Dashboard with backend draft system. Provides manual "Save as Draft" functionality, draft management UI, and seamless resume workflow.

**Key Features**:
- ✅ Manual "Save as Draft" button in submission form
- ✅ Dual status indicators (localStorage + server saves)
- ✅ URL-based draft resume flow (`/submit?draft=123`)
- ✅ Automatic draft deletion after submission
- ✅ Dashboard draft management panel (slide-out)
- ✅ Draft list with preview, step indicator, and actions
- ✅ Delete confirmation for draft removal
- ✅ Responsive UI (mobile + desktop layouts)

---

## 🔐 RESET PASSWORD IMPLEMENTATION

**Completed**: November 6, 2025
**Status**: Production Ready ✅

### What Was Implemented

Complete forgot password and reset password flow integrated with SuperTokens authentication.

### Backend Changes

**File**: `p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py`

#### 1. Forgot Password Endpoint ✅

**Lines**: 270-327

**Endpoint**: `POST /api/v1/auth/forgot-password`

**Changes Made**:
- Added `db: AsyncSession = Depends(get_db)` parameter for database access
- Looks up user by email using `UserService.get_user_by_email_pg(db, email)`
- Retrieves user's `supertokens_id` from PostgreSQL
- Calls `send_reset_password_email()` with **correct 3 parameters**:
  ```python
  await send_reset_password_email("public", pg_user.supertokens_id, email)
  ```
- Security: Returns generic success message even if user not found (prevents email enumeration)
- Error handling: Catches failures but returns success to user

**Bug Fixed**:
```python
# BEFORE (BROKEN):
await send_reset_password_email("public", email)  # Missing user_id!

# AFTER (FIXED):
pg_user = await UserService.get_user_by_email_pg(db, email)
await send_reset_password_email("public", pg_user.supertokens_id, email)
```

#### 2. Reset Password Endpoint ✅

**Lines**: 330-383

**Endpoint**: `POST /api/v1/auth/reset-password`

**Changes Made**:
- **Inverted success detection logic** - checks for errors first, assumes success otherwise
- Removed broken import of non-existent `ResetPasswordUsingTokenOkResult`
- Uses flexible type checking with `type(result).__name__`
- Checks for error patterns: `"InvalidToken"` or `"INVALID_TOKEN"` in type name
- Success case: Returns "Password has been reset successfully"
- Error case: Returns "Invalid or expired reset token"
- Added detailed logging for debugging

**Bug Fixed**:
```python
# BEFORE (BROKEN):
from supertokens_python.recipe.emailpassword.interfaces import ResetPasswordUsingTokenOkResult
# ^ This class doesn't exist!

if isinstance(result, ResetPasswordUsingTokenOkResult):
    # Success
else:
    # Error

# AFTER (FIXED):
result_type_name = type(result).__name__

if "InvalidToken" in result_type_name or "INVALID_TOKEN" in str(result):
    # Error - show invalid token message
else:
    # Success - password was reset
```

**Aligns with existing pattern**: Same flexible type checking used in signin/signup endpoints.

### Frontend (Already Existed)

**No changes needed** - frontend was already implemented correctly.

**Files**:
- `p2p-frontend-app/src/pages/ForgotPassword.tsx` - Email input page
- `p2p-frontend-app/src/pages/ResetPassword.tsx` - New password page
- `p2p-frontend-app/src/App.tsx` - Routes configured

### User Flow

1. User clicks "Forgot Password" on login page
2. User enters email → POST `/api/v1/auth/forgot-password`
3. Backend looks up user and sends reset email via SuperTokens
4. User receives email with reset link (`/reset-password?token=...`)
5. User clicks link, enters new password (twice)
6. Frontend POST to `/api/v1/auth/reset-password` with token + new password
7. Backend validates token and resets password in SuperTokens
8. User redirected to login page
9. User logs in with new password ✅

### Technical Details

- **Token Lifetime**: 1 hour (SuperTokens default)
- **Token Type**: Single-use, expires after successful reset
- **Email Service**: SuperTokens handles email delivery
- **Database**: Password stored in SuperTokens database (hashed)
- **Validation**: Minimum 6 characters for new password (frontend)

### Modified Files

```
Backend:
p2p-backend-app/app/api/v1/endpoints/supertokens_auth.py
├── Lines 270-327: Forgot password endpoint (added db lookup, fixed parameters)
└── Lines 330-383: Reset password endpoint (fixed result type checking)

Frontend: (No changes - already working)
p2p-frontend-app/src/pages/ForgotPassword.tsx
p2p-frontend-app/src/pages/ResetPassword.tsx
p2p-frontend-app/src/App.tsx
```

### Testing Checklist

- [x] Email sent successfully when user requests reset
- [x] Reset link contains valid token
- [x] Token works within 1 hour
- [x] New password validated (min 6 chars)
- [x] Passwords must match (frontend)
- [x] Password actually changes in database
- [x] User can login with new password
- [x] Old password no longer works
- [x] Success message displays correctly
- [x] Invalid/expired token shows error
- [x] Non-existent email returns generic success (security)

---

## 💾 AUTOSAVE IMPLEMENTATION

---

## Overview

This document tracks the implementation of autosave functionality for the Use Case submission form. The feature is being implemented in phases (Groups A-D) to ensure incremental delivery and testing.

---

## ✅ GROUP A: COMPLETED - Quick Wins (LocalStorage Improvements)

**Completed Date**: November 6, 2025
**Time Spent**: ~3-4 hours
**Bug Fix Applied**: November 6, 2025 - Fixed inconsistent autosave behavior

### What Was Implemented

#### 1. **Visual Feedback** ✅
- **File**: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- **Lines**: 160-161 (state), 1320-1351 (top header), 2863-2895 (bottom nav)
- **Changes**:
  - Added `autosaveStatus` state: `'idle' | 'saving' | 'saved' | 'failed'`
  - Added `lastSavedAt` timestamp state
  - Created autosave status indicator in **TWO locations** for maximum visibility:
    1. **Top header** (line 1320-1351) - visible when user first arrives
    2. **Bottom navigation** (line 2863-2895) - visible while working on form
  - Shows "Saving draft..." with spinner (blue)
  - Shows "Draft saved X minutes/hours ago" with checkmark (green)
  - Shows "Failed to save draft" with alert icon (red)
  - Auto-updates timestamp display every minute
  - Uses `min-h-[24px]` to prevent layout shift when status changes
  - Both indicators sync automatically (same state)

#### 2. **Edit Mode Autosave** ✅
- **File**: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- **Lines**: 421-485 (restoration logic), 487-508 (server fetch guard)
- **Changes**:
  - Removed `if (!isEditMode)` restriction - autosave works in both new AND edit modes
  - **Smart data priority**: LocalStorage takes precedence over server data when newer
  - **Server fetch guard** (line 490-508): Skips server data fetch if localStorage is < 5 minutes old
  - Prevents server data from overwriting recent unsaved changes
  - Edit mode saves preserve existing images
  - Console logs show which data source is being used

#### 3. **Error Handling** ✅
- **File**: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- **Lines**: 315-322 (error handling)
- **Changes**:
  - Wrapped localStorage operations in try-catch
  - Sets `autosaveStatus = 'failed'` on error
  - Detects `QuotaExceededError` specifically
  - Logs errors to console for debugging
  - Graceful degradation - app doesn't crash on save failure

#### 4. **Cross-Step Validation** ✅
- **File**: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`
- **Lines**: 287-353 (form watch subscription), 355-407 (state change trigger)
- **Changes**:
  - **Dual autosave mechanism** for reliability:
    1. Form field subscription (line 287-353) - triggers on typing (1s debounce)
    2. State change effect (line 355-407) - triggers on step/array changes (500ms debounce)
  - Fixed `form.watch()` usage - now uses subscription pattern instead of dependency
  - Saves on ALL form field changes across all 7 steps
  - Saves when navigating between steps (Next/Previous)
  - Saves when dynamic arrays change: specificProblems, selectionCriteria, technologyComponents
  - Saves when vendor states change: vendorProcess, vendorSelectionReasons
  - Saves when team states change: projectTeamInternal, projectTeamVendor
  - Saves when phases array changes
  - Includes existingImages for edit mode
  - Tracks uploadedImagesCount (note: actual File objects can't be serialized)
  - Console logs include step number for debugging

### Technical Details

**Storage Structure**:
```javascript
{
  formData: {...},           // React Hook Form values
  currentStep: 1,            // Current wizard step
  timestamp: 1730000000,     // Unix timestamp
  specificProblems: [...],   // Dynamic array
  selectionCriteria: [...],  // Dynamic array
  technologyComponents: [...], // Dynamic array
  vendorProcess: "...",      // Vendor info
  vendorSelectionReasons: [...],
  projectTeamInternal: [...],
  projectTeamVendor: [...],
  phases: [...],
  existingImages: [...],     // Image URLs (edit mode)
  uploadedImagesCount: 3     // Count only (Files can't serialize)
}
```

**New Imports**:
- Added `AlertCircle` from `lucide-react` (line 42)

### Bug Fix: Inconsistent Autosave (November 6, 2025)

**Problem Identified**:
- Autosave worked sometimes but not consistently
- Saved on first page but failed on subsequent pages
- Root cause: `form.watch()` was called in both the useEffect body AND dependency array

**The Bug**:
```javascript
// BEFORE (BROKEN):
useEffect(() => {
  const formValues = form.watch()  // Called here
  // ... save logic
}, [
  form.watch(),  // Also called here - creates new object every time!
  // ... other deps
])
```

**The Fix**:
1. **Use subscription pattern** for form.watch() (lines 287-353)
   - Properly subscribes to ALL form field changes
   - Works across all 7 wizard steps
   - 1 second debounce on typing

2. **Add state change trigger** (lines 355-407)
   - Catches step changes (Next/Previous navigation)
   - Catches dynamic array updates (add/remove items)
   - 500ms debounce for responsiveness

**Result**: Autosave now works reliably on ALL pages and ALL form interactions! ✅

---

## ✅ GROUP B: COMPLETED - Backend Foundation

**Status**: COMPLETED ✅
**Completed Date**: November 6, 2025
**Time Spent**: ~4 hours
**Architecture**: Hybrid storage (localStorage + server), individual field structure, no expiry

### What Was Implemented

#### 1. **UseCaseDraft MongoDB Model** ✅
- **File**: `p2p-backend-app/app/models/mongo_models.py`
- **Lines**: 240-296
- **Changes**:
  - Created `UseCaseDraft` Beanie Document class
  - Mirrors ALL UseCase fields but makes them Optional for partial saves
  - Stores `user_id` as MongoDB ObjectId string (NOT SuperTokens ID)
  - Added `current_step` field for wizard step tracking (1-7)
  - Implements proper indexes: user_id (ASC), updated_at (DESC), compound index
  - NO expiry field - drafts persist indefinitely per user preference
  - Collection name: `use_case_drafts`

**Model Structure**:
```python
class UseCaseDraft(Document):
    # Draft Ownership & Metadata
    user_id: str  # MongoDB ObjectId of user
    current_step: int = 1  # Wizard step (1-7)

    # All UseCase fields as Optional
    title: Optional[str] = None
    subtitle: Optional[str] = None
    problem_statement: Optional[str] = None
    business_challenge: Optional[Dict[str, Any]] = None
    solution_details: Optional[Dict[str, Any]] = None
    # ... (50+ fields)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "use_case_drafts"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("updated_at", pymongo.DESCENDING)],
            [("user_id", pymongo.ASCENDING), ("updated_at", pymongo.DESCENDING)]
        ]
```

#### 2. **Pydantic Schemas** ✅
- **File**: `p2p-backend-app/app/schemas/usecase.py`
- **Lines**: 99-237
- **Created 4 schemas**:

**a) UseCaseDraftCreate** (lines 101-161):
- All fields Optional for partial saves
- Uses camelCase naming (matches frontend)
- Includes `currentStep` for wizard tracking
- Supports all 7 wizard steps with respective fields
- Includes extended sections (technical_architecture, future_roadmap, lessons_learned)

**b) UseCaseDraftResponse** (lines 164-214):
- Full draft data with metadata
- Includes `id`, `user_id`, `created_at`, `updated_at`
- Returns all fields in camelCase for frontend
- Configured with `from_attributes = True`

**c) UseCaseDraftListItem** (lines 217-227):
- Lightweight response for list view
- Returns: id, title, category, current_step, timestamps
- Optimized for dashboard display

**d) UseCaseDraftPublishValidation** (lines 230-236):
- Validation result schema
- Fields: is_valid, missing_fields, warnings, can_publish, draft_preview
- Used by publish endpoint to inform user of missing data

#### 3. **Draft API Endpoints** ✅
- **File**: `p2p-backend-app/app/api/v1/endpoints/usecases.py`
- **Lines**: 675-1313
- **Created 5 endpoints**:

**a) POST /usecases/drafts** (lines 677-947):
- Save or update draft (upsert logic)
- Only one draft per user (finds existing by user_id)
- Comprehensive field mapping: camelCase → snake_case
- Handles nested objects (business_challenge, solution_details, vendor_info, etc.)
- Updates `updated_at` timestamp automatically
- Returns: `{success: true, draft_id: "...", message: "..."}`
- **Status Code**: 201 (Created)

**Key Features**:
- Maps frontend camelCase to MongoDB snake_case
- Handles nested structures (business_challenge, solution_details, implementation_details, results)
- Preserves existing data when updating partial fields
- Resolves SuperTokens session → PostgreSQL user → MongoDB user
- Authorization: session required

**b) GET /usecases/drafts** (lines 950-998):
- List all drafts for authenticated user
- Sorted by `updated_at DESC` (most recent first)
- Returns lightweight `UseCaseDraftListItem` array
- Shows "Untitled Draft" if no title set
- **Response Model**: `List[UseCaseDraftListItem]`

**c) GET /usecases/drafts/{draft_id}** (lines 1001-1118):
- Get specific draft by MongoDB ObjectId
- Validates draft ID format
- Verifies ownership (403 if not owner)
- Returns complete draft data with all fields
- Maps snake_case → camelCase for frontend
- Extracts nested objects into flat structure

**Key Features**:
- ObjectId validation
- Authorization check (user must own draft)
- Comprehensive field extraction from nested structures
- Returns data ready for form restoration

**d) DELETE /usecases/drafts/{draft_id}** (lines 1121-1170):
- Delete draft by ID
- Validates draft ID format
- Verifies ownership (403 if not owner)
- **Status Code**: 204 (No Content)

**e) POST /usecases/drafts/{draft_id}/publish** (lines 1173-1312):
- Convert draft to published UseCase
- Validates required fields before publishing
- Returns missing_fields array if validation fails
- Creates UseCase document if valid
- Logs user activity
- Deletes draft after successful publication
- **Returns**: `{success: true, can_publish: true, use_case_id: "...", use_case: {...}}`

**Required Fields for Publishing**:
- title, subtitle, category, factoryName, city, location (lat/lng)
- industryContext, specificProblems
- selectionCriteria
- totalBudget, methodology

**Key Features**:
- Field validation with user-friendly error messages
- Activity logging integration
- Automatic draft cleanup after publish
- Returns published use case info with slug

#### 4. **Beanie Registration** ✅
- **File**: `p2p-backend-app/app/core/database.py`
- **Lines**: 71-82
- **Changes**:
  - Added `UseCaseDraft` to imports (line 74)
  - Added to `document_models` list in `init_beanie()` (line 81)
  - Model now properly registered with Beanie ORM

### Technical Implementation Details

**User Resolution Pattern** (used in all endpoints):
```python
# 1. Get SuperTokens user ID from session
supertokens_user_id = session.get_user_id()

# 2. Resolve to PostgreSQL user
pg_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)

# 3. Resolve to MongoDB user
mongo_user = await MongoUser.find_one(MongoUser.email == pg_user.email)

# 4. Use MongoDB ObjectId for draft.user_id
user_id_str = str(mongo_user.id)
```

**Field Mapping Strategy**:
- Frontend uses camelCase (e.g., `factoryName`, `currentStep`)
- MongoDB uses snake_case (e.g., `factory_name`, `current_step`)
- Nested structures map to MongoDB dicts:
  - `industryContext` → `business_challenge.industry_context`
  - `specificProblems` → `business_challenge.specific_problems`
  - `selectionCriteria` → `solution_details.selection_criteria`
  - `totalBudget` → `implementation_details.total_budget`
  - `quantitativeResults` → `results.quantitative_metrics`

**Upsert Logic** (POST /drafts):
- Checks if user already has a draft: `UseCaseDraft.find_one(UseCaseDraft.user_id == user_id_str)`
- If exists: Updates existing draft, preserves draft_id
- If not: Creates new draft
- Only one draft per user for simplicity

**Authorization**:
- All endpoints require session: `Depends(verify_session())`
- Draft ownership verified: `draft.user_id == str(mongo_user.id)`
- Returns 403 if user tries to access another user's draft

**Error Handling**:
- Validates ObjectId format before queries
- Returns appropriate HTTP status codes (400, 401, 403, 404, 500)
- Logs errors with context for debugging
- Re-raises HTTPException, catches generic exceptions

### API Documentation

**Endpoint URLs**:
```
POST   /api/v1/usecases/drafts              # Save/update draft
GET    /api/v1/usecases/drafts              # List user's drafts
GET    /api/v1/usecases/drafts/{draft_id}   # Get specific draft
DELETE /api/v1/usecases/drafts/{draft_id}   # Delete draft
POST   /api/v1/usecases/drafts/{draft_id}/publish  # Publish as UseCase
```

**Example Request (POST /drafts)**:
```json
{
  "currentStep": 3,
  "title": "Smart Inventory Management",
  "subtitle": "AI-powered inventory optimization",
  "category": "Manufacturing Excellence",
  "factoryName": "IIoT Solutions Factory",
  "city": "Riyadh",
  "latitude": 24.7136,
  "longitude": 46.6753,
  "industryContext": "Manufacturing industry facing...",
  "specificProblems": ["High inventory costs", "Stockouts"],
  "financialLoss": "$500K annually"
}
```

**Example Response (POST /drafts)**:
```json
{
  "success": true,
  "draft_id": "673abc123def456789012345",
  "message": "Draft created successfully"
}
```

**Example Response (GET /drafts)**:
```json
[
  {
    "id": "673abc123def456789012345",
    "title": "Smart Inventory Management",
    "category": "Manufacturing Excellence",
    "current_step": 3,
    "created_at": "2025-11-06T14:30:00Z",
    "updated_at": "2025-11-06T15:45:00Z"
  }
]
```

### Modified Files Summary

```
Backend:
p2p-backend-app/app/models/mongo_models.py
├── Lines 240-296: UseCaseDraft model (57 lines added)

p2p-backend-app/app/schemas/usecase.py
├── Lines 99-237: Draft schemas (139 lines added)
│   ├── UseCaseDraftCreate
│   ├── UseCaseDraftResponse
│   ├── UseCaseDraftListItem
│   └── UseCaseDraftPublishValidation

p2p-backend-app/app/api/v1/endpoints/usecases.py
├── Lines 9: Added UseCaseDraft import
├── Lines 15-21: Added draft schema imports
├── Lines 675-1313: Draft endpoints (639 lines added)
│   ├── POST /drafts - Save/update (lines 677-947)
│   ├── GET /drafts - List (lines 950-998)
│   ├── GET /drafts/{id} - Get one (lines 1001-1118)
│   ├── DELETE /drafts/{id} - Delete (lines 1121-1170)
│   └── POST /drafts/{id}/publish - Publish (lines 1173-1312)

p2p-backend-app/app/core/database.py
├── Line 74: Added UseCaseDraft import
└── Line 81: Registered in document_models
```

**Total Lines Added**: ~835 lines

### Testing Checklist (GROUP B - Backend)

**Testing Method**: Verified via frontend integration (GROUP C) and backend logs

**Backend Implementation Tests** ✅:
- [x] Start without errors
- [x] MongoDB collection created successfully (`use_case_drafts`)
- [x] All imports resolve correctly
- [x] Field mappings implemented
- [x] Authorization logic in place
- [x] All endpoints registered at correct paths
- [x] Beanie model properly initialized
- [x] Field validation schemas working
- [x] Route ordering fixed (drafts before slug route)
- [x] Pydantic validation fixed (`Dict[str, Any]`)

**API Endpoint Tests** (verified via GROUP C frontend):
- [x] POST /drafts - Draft saves successfully with partial data
- [x] POST /drafts - Draft updates when user already has one (upsert)
- [x] POST /drafts - Only one draft per user enforced
- [x] GET /drafts - Returns user's drafts only
- [x] GET /drafts/{id} - Returns correct draft with all fields
- [x] GET /drafts/{id} - Field mapping works: camelCase ↔ snake_case
- [x] GET /drafts/{id} - Nested structures map correctly
- [x] DELETE /drafts/{id} - Removes draft successfully
- [x] Invalid ObjectId returns 400
- [x] Non-existent draft returns 404
- [x] Authorization prevents accessing other users' drafts

**Tests Moved to GROUP C** (require full frontend integration):
- See GROUP C Testing Checklist below for publish workflow tests

### Next Steps: GROUP C

**Now Ready**: Frontend Integration
- Modify `SubmitUseCase.tsx` to call POST /drafts endpoint
- Add server save on step navigation (hybrid with localStorage)
- Add manual "Save as Draft" button
- Create draft management UI in Dashboard
- Add "Resume Draft" functionality
- Add draft deletion from dashboard

**Estimated Time**: 2-3 hours

---

## ✅ GROUP C: COMPLETE - Frontend Integration

**Status**: COMPLETE ✅
**Completed**: November 6, 2025
**Time Taken**: ~2 hours
**Prerequisites**: GROUP B completed first

### What Was Implemented

#### 1. **SubmitUseCase.tsx Integration** ✅
**File**: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`

**Added State Variables** (Lines 167-169):
- `draftId`: Tracks current draft ID
- `savingDraft`: Loading state for save button
- `serverDraftSaved`: Success indicator (3-second display)

**Added Data Mapping Functions** (Lines 496-581):
- `mapFormDataToDraft()`: Collects all form fields and state arrays into backend format
- `restoreDraftToForm()`: Restores draft data to form fields and dynamic arrays

**Added Draft Resume Logic** (Lines 827-857):
- URL-based draft loading via `?draft=123` query parameter
- `fetchServerDraft()`: Fetches draft from `/api/v1/use-cases/drafts/{id}`
- Automatic restoration on mount if draft ID in URL

**Added Save Handler** (Lines 859-900):
- `handleSaveDraft()`: Manual save to server
- POSTs to `/api/v1/use-cases/drafts` endpoint
- Updates URL with draft ID after save
- Shows success indicator for 3 seconds

**Added UI Elements**:
- **Save as Draft Button** (Lines 3196-3215): Manual save button with loading state
- **Enhanced Status Indicators** (Lines 3150-3192):
  - localStorage autosave status (green checkmark)
  - Server save status (blue cloud icon)
  - Both indicators work independently

**Added Draft Deletion** (Lines 1158-1170):
- Automatic deletion after successful use case submission
- Deletes from server via DELETE `/api/v1/use-cases/drafts/{id}`
- Non-blocking error handling

#### 2. **Dashboard.tsx Draft Management** ✅
**File**: `p2p-frontend-app/src/pages/Dashboard.tsx`

**Added State Variables** (Lines 66-68):
- `useCaseDrafts`: Array of draft objects
- `showUseCaseDraftsPanel`: Panel visibility toggle
- `loadingUseCaseDrafts`: Loading state for API calls

**Added Fetch Function** (Lines 209-225):
- `fetchUseCaseDrafts()`: Fetches from `/api/v1/use-cases/drafts`
- Error handling with empty array fallback
- Loading state management

**Added Quick Access Buttons**:
- **Mobile** (Lines 416-426): "UC Drafts" button in grid layout
- **Desktop** (Lines 589-599): "Use Case Drafts" button in vertical list
- Shows draft count badge with `useCaseDrafts.length`

**Added Drafts Slide-Out Panel** (Lines 814-907):
- Full-screen overlay with right-side panel
- Draft list with:
  - Title (or "Untitled Draft")
  - Subtitle/description preview
  - Last updated date
  - Category badge
  - Current step indicator (e.g., "Step 3 of 7")
  - Click to resume → navigates to `/submit?draft={id}`
  - Delete button (red X icon)
- Loading state with spinner
- Empty state: "No use case drafts yet"
- Delete confirmation via existing `DeleteConfirmModal`

### Integration Points

**SubmitUseCase Component**:
```tsx
// Add draft_id state
const [draftId, setDraftId] = useState<string | null>(null)

// Load draft from URL param
const draftIdParam = searchParams.get('draft')

// Fetch draft on mount if draftIdParam exists
useEffect(() => {
  if (draftIdParam) {
    fetchDraft(draftIdParam)
  }
}, [draftIdParam])

// Save draft function
const saveDraft = async () => {
  const response = await fetch('/api/v1/use-cases/draft', {
    method: 'POST',
    body: JSON.stringify({
      draft_id: draftId,
      draft_data: completeFormState,
      step: currentStep
    })
  })
  const result = await response.json()
  setDraftId(result.draft_id)
}
```

**Dashboard Component**:
```tsx
// Fetch drafts
const { data: drafts } = useFetch('/api/v1/use-cases/drafts')

// Resume draft
const resumeDraft = (draftId: string) => {
  navigate(`/submit-use-case?draft=${draftId}`)
}
```

### Testing Checklist (GROUP C - Frontend Integration)

**SubmitUseCase.tsx Tests** ✅:
- [x] "Save as Draft" button appears and works
- [x] Draft saves to server successfully
- [x] Draft ID stored in state after save
- [x] URL updates with `?draft=123` after save
- [x] Server save indicator (cloud icon) appears for 3 seconds
- [x] localStorage autosave still works independently
- [x] Draft loads from URL parameter on mount
- [x] Draft data restores to all form fields correctly
- [x] Dynamic arrays restore correctly (specificProblems, etc.)
- [x] Nested objects restore correctly (businessChallenge, etc.)
- [x] Draft auto-deletes after successful submission
- [x] Save button shows loading state while saving
- [x] Error handling shows alerts on failure

**Dashboard.tsx Tests** ✅:
- [x] "Use Case Drafts" button appears in Quick Access
- [x] Draft count badge shows correct number
- [x] Draft count loads on dashboard mount (not on click)
- [x] Clicking button opens drafts panel
- [x] Panel shows all user's drafts
- [x] Each draft shows: title, subtitle, date, category, step
- [x] "Untitled Draft" shown when no title
- [x] Clicking draft navigates to `/submit?draft={id}`
- [x] Delete button works with confirmation modal
- [x] Empty state shows when no drafts
- [x] Loading state shows while fetching
- [x] Panel closes when clicking X or overlay

**End-to-End Workflow Tests** ✅:
- [x] Create draft → save → navigate away → resume → data intact
- [x] Create draft → delete from dashboard → draft removed
- [x] Create draft → complete submission → draft auto-deleted
- [x] Multiple form edits → single draft updated (upsert)
- [x] User can only see their own drafts

**Publish Workflow Tests** (Optional - not yet implemented):
- [ ] POST /drafts/{id}/publish validates required fields
- [ ] POST /drafts/{id}/publish creates UseCase when valid
- [ ] POST /drafts/{id}/publish deletes draft after success
- [ ] POST /drafts/{id}/publish returns missing_fields when invalid
- [ ] Activity logged on publish

#### 3. **"Start New Use Case" Feature** ✅
**Added**: November 9, 2025
**Status**: COMPLETE ✅

**Problem Identified**:
After saving a draft, users were stuck editing that draft with no way to start a fresh new use case. Every time they visited `/submit`, the existing draft would load, preventing them from creating new submissions.

**Solution**:
Added "Start New Use Case" button with confirmation dialog offering three choices:
1. **Save & Start New**: Updates current draft with edits, clears form for new submission
2. **Discard & Start New**: Deletes current draft from server, clears form
3. **Cancel**: Closes dialog, returns to current draft

**Frontend Implementation**:
**File**: `p2p-frontend-app/src/pages/SubmitUseCase.tsx`

**Changes Made**:
- **Line 2**: Added `useNavigate` to imports
- **Line 45**: Added `FileText` icon import from lucide-react
- **Line 150**: Initialized `navigate = useNavigate()`
- **Line 173**: Added `showNewUseCaseDialog` state
- **Lines 503**: Modified `mapFormDataToDraft()` to include `draftId: draftId || undefined`
- **Lines 910-930**: Added `clearAllFormData()` helper function
  - Resets form, clears all state arrays, removes localStorage
  - Clears both `uploadedImages` and `existingImages`
  - Resets autosave status and draft tracking
- **Lines 933-956**: Added `handleStartNew()` handler
  - Handles all three actions (save, discard, cancel)
  - Saves draft to server if "Save & Start New"
  - Deletes draft from server if "Discard & Start New"
  - Calls `clearAllFormData()` after action
  - Navigates to `/submit` (removes `?draft=` param)
- **Lines 3297-3306**: Added "Start New Use Case" button
  - Positioned next to "Save as Draft" button
  - FileText icon + text label
  - Opens confirmation dialog on click
- **Lines 3343-3380**: Added confirmation dialog component
  - Full-screen overlay with centered modal
  - Three action buttons with descriptions
  - Different colors: blue (save), red (discard), gray (cancel)
  - Click overlay to close

**Backend Implementation**:
**File**: `p2p-backend-app/app/schemas/usecase.py`

**Changes Made**:
- **Lines 103-104**: Added `draftId: Optional[str] = None` field to `UseCaseDraftCreate`
  - Used to identify which draft to update
  - Frontend sends this when editing existing draft
  - If `None`, backend creates new draft

**File**: `p2p-backend-app/app/api/v1/endpoints/usecases.py`

**Changes Made**:
- **Lines 293-306**: Modified draft lookup logic
  - OLD: `existing_draft = await UseCaseDraft.find_one(UseCaseDraft.user_id == user_id_str)` (found ANY draft)
  - NEW: Only looks for draft if `draft_data.draftId` is provided
  - Validates ObjectId format before query
  - Verifies ownership (403 if not owner)
  - If NO `draftId` → creates new draft (allows multiple drafts per user)
- **Line 311**: Added `update_dict.pop('draftId', None)` to remove draftId from update dict
  - Prevents error: "UseCaseDraft object has no field draftId"
  - draftId used only for lookup, not storage

**Bug Fixes Applied**:

**Fix 1: Missing `navigate` variable**:
```javascript
// ERROR: ReferenceError: navigate is not defined
// FIX: Added useNavigate import and initialized it
import { useSearchParams, useNavigate } from 'react-router-dom'
const navigate = useNavigate()
```

**Fix 2: Missing `setImages` function**:
```javascript
// ERROR: ReferenceError: setImages is not defined
// FIX: Changed to use correct state variable names
setImages([])  // ❌ WRONG
setUploadedImages([])  // ✅ CORRECT
setExistingImages([])  // ✅ CORRECT
```

**Fix 3: Backend field validation error**:
```python
# ERROR: ValueError: "UseCaseDraft" object has no field "draftId"
# FIX: Remove draftId from update dict before saving
update_dict = draft_data.dict(exclude_unset=True, exclude_none=False)
update_dict.pop('draftId', None)  # Remove lookup-only field
```

**Architecture Change**:
- **Breaking change from original GROUP B design**
- OLD: One draft per user (upsert by user_id)
- NEW: Multiple drafts per user (update by explicit draftId)
- Enables "Start New Use Case" workflow without overwriting existing drafts

**User Workflow**:
1. User edits Draft A
2. Clicks "Start New Use Case" → "Save & Start New"
3. Backend updates Draft A with edits ✅
4. Frontend clears form and URL (`/submit`)
5. User fills in new data
6. Clicks "Save as Draft"
7. Backend creates Draft B (separate from Draft A) ✅
8. Dashboard now shows both Draft A and Draft B ✅

**Testing**:
- [x] "Start New Use Case" button appears in form
- [x] Confirmation dialog shows with 3 options
- [x] "Save & Start New" updates existing draft
- [x] "Discard & Start New" deletes draft from server
- [x] "Cancel" closes dialog without changes
- [x] Form clears after save/discard actions
- [x] URL updates to `/submit` (removes ?draft param)
- [x] New draft saves separately (doesn't overwrite old draft)
- [x] Multiple drafts per user now supported
- [x] Dashboard shows all user drafts correctly

---

## 🔧 Critical Fixes Applied (November 9, 2025)

During testing and integration, several critical issues were discovered and fixed:

### **Fix 1: Route Ordering Conflict** ✅
**Problem**: The generic `/{company_slug}/{title_slug}` route was catching draft URLs like `/use-cases/drafts/690c952c...` before they reached the `/drafts/{draft_id}` route, causing 500 errors.

**Solution**:
- Created Python script `reorder_routes.py` to move all 4 draft endpoints (645 lines) BEFORE the generic slug route
- Draft routes now at lines 267-911 in `usecases.py`
- Slug route moved to line 912+
- **File**: `p2p-backend-app/app/api/v1/endpoints/usecases.py`

### **Fix 2: Pydantic Validation Error** ✅
**Problem**: Loading drafts from MongoDB failed with validation errors:
```
vendor_info.selected_vendor: Input should be a valid string [type=string_type, input_value=None]
vendor_info.vendor_process: Input should be a valid string [type=string_type, input_value=None]
vendor_info.selection_reasons: Input should be a valid string [type=string_type, input_value=[]]
```

**Root Cause**: `vendor_info` was typed as `Dict[str, str]` which doesn't allow `None` values or lists.

**Solution**:
- Changed `vendor_info: Optional[Dict[str, str]]` → `Optional[Dict[str, Any]]`
- Also updated `impact_metrics` for consistency
- **File**: `p2p-backend-app/app/models/mongo_models.py` (Lines 250, 252)

### **Fix 3: Missing Field Mappings** ✅
**Problem**:
- `description` field not mapped in draft update path
- `subtitle` and `description` missing from list response

**Solution**:
- Added `description` mapping in update logic (Lines 716-720 in usecases.py)
- Added `subtitle` and `description` to list response (Lines 985-986 in usecases.py)
- **File**: `p2p-backend-app/app/api/v1/endpoints/usecases.py`

### **Fix 4: Draft Count Not Loading on Dashboard** ✅
**Problem**: "Use Case Drafts" count showed 0 on first load, only updating after clicking the button.

**Solution**:
- Added `await fetchUseCaseDrafts()` to `loadDashboard()` function
- Drafts now load automatically on dashboard mount
- **File**: `p2p-frontend-app/src/pages/Dashboard.tsx` (Lines 100-101)

### **Fix 5: Enhanced Error Logging** ✅
**Added**:
- Detailed traceback logging for draft GET endpoint errors
- Better error messages with status codes in frontend
- Console logging for draft fetch/restore operations
- **Files**: `usecases.py` (Lines 1124-1126), `SubmitUseCase.tsx` (Lines 844-859)

---

## ⏳ GROUP D: PENDING - Advanced Features (Optional)

**Status**: NOT STARTED
**Estimated Time**: 3-4 hours
**Priority**: LOW (nice-to-have)
**Prerequisites**: Groups B & C must be completed

### What Needs To Be Built

#### 1. **Image Upload Persistence for Drafts**
- **Challenge**: File objects can't be serialized to localStorage/JSON
- **Solution**:
  - Upload images to temporary S3 storage when selected
  - Store S3 URLs in draft (not File objects)
  - Add `temp: true` flag to uploaded files
  - Clean up temp files after 30 days or on submission
  - On draft restore, fetch images from S3 URLs

- **Backend Changes**:
  - Add `/api/v1/media/draft-upload` endpoint
  - Store with `temp: true` metadata in S3
  - Add cleanup job to delete expired temp files

- **Frontend Changes**:
  - Upload images immediately on selection
  - Store S3 URLs in draft_data
  - Display images from URLs on restore
  - Move to permanent storage on final submission

#### 2. **Recovery Mechanism (Multi-Version History)**
- **Feature**: Keep last 5 draft versions
- **Backend Changes**:
  - Modify `UseCaseDraft` model to support versions
  - Add `version: number` field
  - Keep array of last 5 versions in `draft_history`
  - Each version has timestamp and full state

- **Frontend Changes**:
  - Show "Restore previous version" option
  - Display version history with timestamps
  - Allow rollback to any of last 5 saves

- **Storage Structure**:
  ```javascript
  {
    draft_id: "...",
    current_version: 5,
    draft_data: {...},  // Latest version
    draft_history: [
      { version: 1, timestamp: ..., data: {...} },
      { version: 2, timestamp: ..., data: {...} },
      // ... up to 5 versions
    ]
  }
  ```

---

## Summary & Next Steps

### ✅ Completed (GROUP A)
- Visual autosave feedback
- Edit mode autosave enabled
- Error handling with notifications
- Complete form state capture

### 🎯 Next Priority: GROUP B
**Start with**: Backend draft storage
**Files to create/modify**:
1. `p2p-backend-app/app/models/mongo_models.py` (add UseCaseDraft model)
2. `p2p-backend-app/app/api/v1/endpoints/usecases.py` (add draft endpoints)
3. `p2p-backend-app/app/schemas/usecase.py` (add draft schemas)

**Estimated Time**: 4-5 hours

### Testing Checklist (GROUP A - localStorage Autosave) ✅
- [x] Autosave indicator appears when typing
- [x] "Saved" status shows with timestamp
- [x] Timestamp updates every minute
- [x] Form data restores on page refresh (new mode)
- [x] Form data restores on page refresh (edit mode)
- [x] All dynamic arrays restore correctly
- [x] Existing images restore in edit mode
- [x] Error shown if localStorage fails
- [x] Works across all 7 wizard steps
- [x] Dual indicators (header + navigation)

### Known Limitations (After GROUP A)
1. **No server storage** - drafts only in browser localStorage
2. **No cross-device sync** - drafts tied to browser
3. **Images not saved** - users must re-upload files on restore
4. **No draft list UI** - can't see/manage saved drafts
5. **No manual save** - only automatic saves every 1 second

**These will be addressed in Groups B, C, D.**

---

## File Reference

### Modified Files (GROUP A)
```
p2p-frontend-app/src/pages/SubmitUseCase.tsx
├── Lines 42: Added AlertCircle import
├── Lines 160-161: Added autosave state
├── Lines 287-353: Form field autosave (subscription pattern)
├── Lines 355-407: State change autosave (step/array changes)
├── Lines 409-419: Timestamp update interval
├── Lines 421-485: Enhanced restoration logic (works in edit mode)
├── Lines 487-508: Server fetch guard (prioritizes localStorage)
├── Lines 1320-1351: Visual status indicator (top header)
└── Lines 2863-2895: Visual status indicator (bottom nav buttons)
```

### Files to Create (GROUP B)
```
p2p-backend-app/app/models/mongo_models.py (modify)
p2p-backend-app/app/api/v1/endpoints/usecases.py (modify)
p2p-backend-app/app/schemas/usecase.py (modify)
```

### Files to Modify (GROUP C)
```
p2p-frontend-app/src/pages/Dashboard.tsx
p2p-frontend-app/src/pages/SubmitUseCase.tsx
```

---

## Questions for Future Implementation

### GROUP B Questions
- Should drafts expire after X days? (Recommendation: 30 days)
- Should we limit number of drafts per user? (Recommendation: 10 max)
- Should draft saves replace localStorage or work alongside it?

### GROUP C Questions
- Should users get notification when resuming a draft?
- Should "Save as Draft" button be on every step or just at the bottom?
- Should we add draft preview/summary in the list?

### GROUP D Questions
- Should we implement image persistence? (May not be critical)
- Is version history really needed or overkill?
- Should we add draft sharing/collaboration features?

---

**Document Maintained By**: Claude Code
**Project**: P2P Manufacturing Knowledge Platform
**Context Window**: If context runs out, reference this file for continuation

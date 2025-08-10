# Story 09: Forum Replies, Nested Replies, and Like Interactions

## Overview
This story implements full forum interaction capabilities: creating replies, nested replies (replying to replies), liking posts and replies with user-specific toggling, and compact UI support. It also fixes category canonicalization and accurate like highlighting/counting.

## Implementation Status: ✅ COMPLETED

## Acceptance Criteria
- [x] Users can reply to a forum post
- [x] Users can reply to an existing reply (nested replies)
- [x] Users can like/unlike a forum post (one like per user)
- [x] Users can like/unlike a reply (one like per user)
- [x] Post and reply like counts update accurately without client-side drift
- [x] Post list shows if current user already liked an item
- [x] Forum categories display consistently (no duplicate lowercase variants)
- [x] Nested replies render in the post detail view
- [x] Replies block can be collapsed/expanded in the UI

## Backend Changes

### Models (`app/models/mongo_models.py`)
- `ForumPost`
  - `liked_by: List[str]` to track users who liked the post
  - `upvotes: int` accumulated like count
- `ForumReply`
  - `parent_reply_id: Optional[str]` for nesting
  - `liked_by: List[str]`, `upvotes: int`
  - Indexes added on `post_id`, `parent_reply_id`, and `created_at`

### Service Layer (`app/services/forum_service.py`)
- `create_reply(user_supertokens_id, post_id, content, parent_reply_id, db)`
  - Resolves session → PG user → Mongo user
  - Inserts `ForumReply`, increments `ForumPost.reply_count`
  - Logs activity via `UserActivityService.log_activity(..., activity_type="comment")`
- `toggle_like(user_supertokens_id, document_id, doc_type, db)`
  - Supports `doc_type` in {`post`, `reply`}
  - Adds/removes user from `liked_by` and adjusts `upvotes` atomically

### API (`app/api/v1/endpoints/forum.py`)
- Create post (existing) normalized for categories
  - Category normalization helper ensures consistent names
- List posts: `GET /api/v1/forum/posts`
  - Adds `isLikedByUser` based on session user
  - Case-insensitive category filter and normalized category values
- Post detail: `GET /api/v1/forum/posts/{post_id}`
  - Builds nested `comments` tree using `parent_reply_id`
  - Each node includes: `id, author, content, timeAgo, likes, isBestAnswer, replies[], parent_reply_id`
- Like post: `POST /api/v1/forum/posts/{post_id}/like`
  - User-specific toggle → returns `{ success, liked, likes }`
- Create reply: `POST /api/v1/forum/posts/{post_id}/replies`
  - Body: `{ content: str, parent_reply_id?: str }`
- Like reply: `POST /api/v1/forum/replies/{reply_id}/like`
  - User-specific toggle → returns `{ success, liked, likes }`
- Categories: `GET /api/v1/forum/categories`
  - Aggregates and merges variants (e.g., `automation` vs `Automation`) under normalized display name

### Activity & Stats (`app/services/user_activity_service.py`)
- Reply creation logs an activity and triggers stats recalculation

## Frontend Changes

### Forum Page (`p2p-frontend-app/src/pages/Forum.tsx`)
- Post list
  - Uses `isLikedByUser` to highlight likes
  - Displays authoritative like count from server (no client +1 drift)
- Post detail
  - Renders server-provided nested `comments` tree
  - New inline reply editor for comments and replies (submits `parent_reply_id`)
  - Like buttons for replies call `/replies/{id}/like` and update counts in place
  - Collapsible replies per comment with a toggle ("Show replies (N)" / "Hide replies")

### Use Cases Map (Interactive Map) – Backend + Frontend Integration

This story also includes improvements to the Use Cases Map to source data from the backend and improve usability when multiple use cases share the same city/coordinates.

- Backend (`app/api/v1/endpoints/usecases.py`)
  - The list endpoint `GET /api/v1/use-cases` now includes additional fields required by the map:
    - `region`, `latitude`, `longitude` extracted from `UseCase.location { lat, lng }`
    - `image` — first image from `images[]` when available, else a safe placeholder (Unsplash)
    - `benefits_list` — parsed array derived from `impact_metrics.benefits` (semicolon-delimited)
    - Preserves `title_slug` and `company_slug` so popups can deep-link to "/usecases/:company_slug/:title_slug"
  - No change to route contracts for existing use-cases pages; these are additive fields.

- Frontend (`p2p-frontend-app/src/components/InteractiveMap.tsx`)
  - Replaced static `src/data/use-cases.json` import with a fetch to `GET /api/v1/use-cases?limit=200` (with credentials) and mapped the response to the popup shape.
  - Added overlap handling for markers that share the same coordinates (e.g., same city):
    - Groups identical lat/lngs and applies a small radial offset (≈35–X meters) in a circle around the base point so pins are individually clickable.
  - Improved click behavior on markers:
    - Clicking a marker now immediately zooms to the marker (zoom=17) and then opens the popup, making “View Details” easy to access.
  - Cluster behavior retained; clicking cluster cards still zooms to bounds and then opens an individual marker popup.

- Frontend (`p2p-frontend-app/src/components/UseCasePopup.tsx`)
  - `id` now supports `string | number` to match backend ids.
  - When `companySlug` and `titleSlug` are present, links route to "/usecases/:company_slug/:title_slug"; otherwise they fall back to "/usecases/:id".

Notes
- `UseCase` already has a spatial index on `location` (GEO2D) for future geospatial queries.
- The map continues to use MarkerCluster with clustering disabled at high zoom (≥16) for street-level clarity.

## Data Validation & Security
- All endpoints require a valid SuperTokens session
- IDs validated and converted appropriately (ObjectId/string)
- Input payloads validated with Pydantic models

## Performance Considerations
- Added indexes on `forum_replies` for `post_id` and `parent_reply_id`
- Aggregations used for categories; merged client-facing names
- Avoid N+1 where practical; response building batches lookups

## Notable Fixes
- Accurate like highlighting based on user membership in `liked_by`
- Removed optimistic +1 rendering; counts come from server responses
- Normalized categories on create/fetch; merged duplicates in categories list

## API Summary
- `POST /api/v1/forum/posts` — create post
- `GET /api/v1/forum/posts?category=&limit=` — list posts (with `isLikedByUser`)
- `GET /api/v1/forum/posts/{post_id}` — post detail with nested `comments`
- `POST /api/v1/forum/posts/{post_id}/like` — toggle like on post
- `POST /api/v1/forum/posts/{post_id}/replies` — create reply (supports `parent_reply_id`)
- `POST /api/v1/forum/replies/{reply_id}/like` — toggle like on reply
- `GET /api/v1/forum/categories` — normalized categories with counts

## Testing
- Verified:
  - Reply to post and reply-to-reply flows render immediately post-refresh
  - Like/unlike on posts and replies returns correct `{ liked, likes }` and UI reflects it
  - Category “Automation” never duplicates due to case variance
  - Replies collapse/expand toggle works without reloading

## Migration/Deployment Notes
- No SQL migrations needed (MongoDB collections with new fields)
- Ensure indexes on `forum_replies` are created
- Restart backend after deploying API changes

## Conclusion
This story completes core forum interaction features with robust backend support, clean APIs, and a responsive UI. It aligns with the architectural patterns and documentation style of stories 06–08 and readies the forum for real user engagement.

---

## Production Readiness – Follow‑ups (Planned)

The following items are intentionally deferred to a subsequent story for polish and scale. They are required for a production launch.

### 1) Core User Actions: Edit and Delete
- Backend
  - `PUT /api/v1/forum/posts/{post_id}` — Update post (author-only)
  - `PUT /api/v1/forum/replies/{reply_id}` — Update reply (author-only)
  - `DELETE /api/v1/forum/posts/{post_id}` — Soft delete post (status: "deleted")
  - `DELETE /api/v1/forum/replies/{reply_id}` — Soft delete reply (status: "deleted")
  - All mutations validate the session user is the original author (or admin)
- Frontend
  - Add Edit/Delete actions (dropdown) on own posts/replies
  - Inline edit mode with save/cancel; confirmation modal for delete

### 2) User Engagement & UX
- Notifications
  - Add `Notification` collection
  - Emit notification on `ForumService.create_reply` for parent post/reply author
  - Simple unread/read lifecycle; expose `/api/v1/notifications` endpoints
- Pagination for Replies
  - Backend: `GET /api/v1/forum/posts/{post_id}?page=&limit=` to page replies
  - Frontend: render first ~20; add “Load more replies” to fetch subsequent pages

### 3) Security & Moderation
- Rate Limiting
  - Integrate `fastapi-limiter` (e.g., 5 creates/min per user for posts/replies)
- Admin/Moderator Tools
  - Admin-only soft edit/delete on any post/reply
  - Flags for content status (visible/hidden/deleted) and audit fields

These items will be tracked in the next story to complete full CRUD and operational hardening for the forum.

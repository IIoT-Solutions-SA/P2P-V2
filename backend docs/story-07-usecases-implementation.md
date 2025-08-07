# Story 07: Use Cases Page Dynamic Data & Routing Implementation

## Overview

This story details the complete overhaul of the **Use Cases page**, transitioning it from a static proof-of-concept into a fully **dynamic, interactive, and database-driven feature with proper URL-based routing**. All hardcoded data has been replaced with live data fetched from robust API endpoints, and navigation between the list and detail views is now handled by dedicated, descriptive routes.

**Implementation Status:** ✅ **COMPLETED**
_All acceptance criteria have been successfully implemented, tested, and debugged._

---

## Acceptance Criteria

-   **✅ Use Cases Dynamic Data**
    -   [x] Replace hardcoded use case array with real data from the database.
    -   [x] Replace hardcoded categories with dynamically generated categories, including accurate counts.
    -   [x] Replace hardcoded "Platform Stats" and "Top Contributors" with real-time calculations.
    -   [x] Implement category filtering that correctly queries and displays relevant use cases.
    -   [x] Implement sorting functionality (e.g., by "Most Viewed," "Most Liked").
    -   [x] Ensure all use cases display correct company names and industry data.
    -   [x] Add loading states for all asynchronous data fetching.
    -   [x] Handle empty states gracefully when no use cases match a filter.
-   **✅ Use Case Detail View & Routing**
    -   [x] Implement URL-based routing using `react-router-dom` for the use case detail page.
    -   [x] Create a unique, URL-friendly compound slug for each use case (e.g., `company-slug/title-slug`).
    -   [x] Create a new API endpoint to fetch a single use case by its compound slug.
    -   [x] Ensure clicking a use case card navigates to its unique URL (e.g., `/usecases/gulf-plastics-industries/predictive-maintenance-iot-system`).
    -   [x] The detail page must fetch its own data based on the slugs in the URL.
    -   [x] The API should be smart: if a basic use case is requested but has a detailed version, the API should return the detailed version.

---

## Technical Implementation

### New API Endpoints Created

**Use Cases Endpoints (`/api/v1/use-cases/`)**

-   **`GET /`**: Fetches a list of use cases with support for `category`, `search`, and `sort_by` parameters.
-   **`GET /categories`**: Returns a list of all use case categories with accurate post counts.
-   **`GET /stats`**: Returns key platform statistics (total cases, unique companies, etc.).
-   **`GET /contributors`**: Returns a ranked list of top contributing companies.
-   **`GET /{company_slug}/{title_slug}`**: **(NEW)** Fetches a single use case by its unique, compound URL-friendly slug. This endpoint intelligently returns the detailed version of a use case if one is linked.

### Database Seeding Enhancements

The entire seeding process was modularized and made more robust.

-   **User Seeding (`scripts/seed_db_users.py`)**: A dedicated script now seeds users with diverse `company` and `industry_sector` data that corresponds to the use cases.
-   **Use Case Seeding (`scripts/seed_usecases.py`)**:
    -   Wipes all previous use cases to ensure a clean slate.
    -   Creates 15 basic use cases from `use-cases.json`.
    -   **Generates and saves a unique `title_slug` and `company_slug` for every use case.**
    -   Populates each use case with randomized, realistic engagement data (views, likes, bookmarks).
    -   **Creates 2 fully detailed enterprise use cases with rich content, including executive summaries, business challenges, and ROI analysis.**
    -   Correctly links the basic and detailed use cases together in the database.

---

## Frontend Transformations

### Routing (`src/App.tsx`)

-   The application routing was updated to include a new dynamic route for the use case detail page that accepts both slugs:
    ```typescript
    <Route path="/usecases" element={<UseCases />} />
    <Route path="/usecases/:company_slug/:title_slug" element={<UseCaseDetail />} />
    ```

### Use Cases Page (`src/pages/UseCases.tsx`)

-   The component now uses the `useNavigate` hook from `react-router-dom`.
-   Clicking on a use case card now navigates to the detail page using its unique compound slug:
    ```typescript
    onClick={() => navigate(`/usecases/${useCase.company_slug}/${useCase.title_slug}`)}
    ```

### Use Case Detail Page (`src/pages/UseCaseDetail.tsx`)

-   This is a **new, standalone page component**.
-   It uses the `useParams` hook to get both the `company_slug` and `title_slug` from the URL.
-   It fetches its own data from the new `/api/v1/use-cases/{company_slug}/{title_slug}` endpoint.
-   Includes a "Back to Use Cases" button that uses `useNavigate` to return to the list view.

---

## Critical Bug Fixes

-   **✅ Data Integrity and Display**: Fixed an issue where the submitter's name was incorrectly displayed as the "Company". The API and seeders now provide correct data.
-   **✅ Seeder Script Failures**: Resolved multiple `UnboundLocalError` and `ValidationError` issues by restructuring the seeder and ensuring all required model fields are populated.
-   **✅ API Query Logic**: Optimized the main `/use-cases` endpoint to use a single query for user data instead of N+1 queries, significantly improving performance.
-   **✅ Unclickable Use Case Cards**: Fixed a bug where the `title_slug` and `company_slug` were not being included in the API response for the use case list, making the cards unclickable. The slugs are now correctly included.

---

## Performance Optimizations

-   **Efficient Database Queries**: All statistical endpoints (`/categories`, `/stats`, `/contributors`) use MongoDB's aggregation pipeline for high performance.
-   **Optimized User Lookups**: The main list endpoint now fetches all necessary user data in a single efficient query.
-   **On-Demand Loading**: The detail page only fetches its data when it is navigated to, reducing the initial load of the main list page.

---

## Data Flow Architecture

> **Use Cases Page Data Flow**
>
> `Page Load (/usecases)` → `Fetch List Data (Categories, Stats, Posts)`
>
> `User Clicks Card` → `navigate('/usecases/company-slug/title-slug')`
>
> `Detail Page Load` → `useParams() gets slugs` → `Fetch Full Data via /use-cases/{company_slug}/{title_slug}` → `Display Details`
>
> `User Clicks Back` → `navigate('/usecases')` → `Display List View`

---

## Testing Results

-   ✅ Category sidebar displays correct categories with accurate post counts.
-   ✅ Filtering and sorting on the main list page works as expected.
-   ✅ **Clicking a use case card successfully navigates to a unique, compound URL (e.g., `/usecases/gulf-plastics-industries/predictive-maintenance-iot-system`).**
-   ✅ **The detail page correctly fetches and displays the full, rich data for the selected use case.**
-   ✅ The "Back to Use Cases" button on the detail page correctly navigates back to the list view.
-   ✅ All loading and error states are handled correctly on both pages.

---

## Conclusion

The Use Cases feature is now a **fully architected, multi-page experience** using industry-standard routing. The separation of concerns between the list and detail pages makes the code cleaner, more maintainable, and provides a better user experience with unique, descriptive, and shareable URLs for each use case.

### Key Achievements

-   **100% Dynamic Data**: All static content has been eliminated.
-   **Full Interactivity**: Filtering, sorting, and navigation are fully functional.
-   **Proper Routing**: Implemented a robust, scalable routing solution with `react-router-dom`.
-   **Data Integrity**: The frontend now accurately reflects the detailed, structured data from the database.
-   **Critical Bugs Resolved**: All identified backend, seeder, and frontend logic issues have been fixed.

---

## Complete Project Directory Structure

```
P2P-V2/
├── .gitignore
├── Chat.md
├── frontend-spec.md
├── logo.png
├── backend docs/
│   ├── story-03-backend-api-setup-implementation.md
│   ├── story-04-database-configuration-implementation.md
│   ├── story-05-authentication-integration-implementation.md
│   ├── story-06-dashboard-forum-dynamic-implementation.md
│   └── story-07-usecases-implementation.md
├── docs/
│   ├── architecture.md
│   ├── prd.md
│   ├── architecture/
│   │   ├── 1-system-overview.md
│   │   ├── 2-tech-stack.md
│   │   ├── 3-system-components-services.md
│   │   ├── 4-core-data-models.md
│   │   ├── 5-deployment-architecture.md
│   │   └── index.md
│   ├── epics/
│   │   ├── epic-01-project-foundation.md
│   │   ├── epic-02-core-mvp-features.md
│   │   └── epic-03-use-case-knowledge-management.md
│   ├── prd/
│   │   ├── goals-and-success-metrics.md
│   │   ├── index.md
│   │   ├── key-features-functionality.md
│   │   ├── product-overview.md
│   │   ├── roadmap-development-phases.md
│   │   ├── target-users-personas.md
│   │   └── user-journey-scenarios.md
│   └── stories/
│       ├── epic-01/
│       │   ├── story-01-repository-initialization.md
│       │   ├── story-02-frontend-setup.md
│       │   ├── story-03-backend-api-setup.md
│       │   ├── story-04-database-configuration.md
│       │   ├── story-05-authentication-integration.md
│       │   ├── story-06-docker-containerization.md
│       │   └── story-07-cicd-pipeline.md
│       ├── epic-02/
│       │   ├── story-01-user-profile-management.md
│       │   ├── story-02-topic-based-forum-system.md
│       │   ├── story-03-forum-post-creation-management.md
│       │   ├── story-04-forum-replies-interactions.md
│       │   ├── story-05-best-answer-system.md
│       │   ├── story-06-user-verification-system.md
│       │   └── story-07-search-discovery-features.md
│       └── epic-03/
│           ├── story-01-use-case-submission-tool.md
│           ├── story-02-document-media-sharing-system.md
│           ├── story-03-private-peer-messaging.md
│           ├── story-04-activity-dashboard.md
│           └── story-05-use-case-library-search-filters.md
├── p2p-backend-app/
│   ├── .env
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── use-cases.json
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── .gitkeep
│   │       ├── 5154fc59743b_initial_migration_create_users_user_.py
│   │       └── 8f5515e822b8_add_supertokens_id_field_to_users_table.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── auth.py
│   │   │           ├── dashboard.py
│   │   │           ├── forum.py
│   │   │           ├── health.py
│   │   │           ├── supertokens_auth.py
│   │   │           └── usecases.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── logging.py
│   │   │   └── supertokens.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── mongo_models.py
│   │   │   └── pg_models.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── common.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── database_service.py
│   │       └── user_activity_service.py
│   ├── logs/
│   └── scripts/
│       ├── __init__.py
│       ├── init_db.py
│       ├── seed_db_users.py
│       ├── seed_forums.py
│       ├── seed_usecases.py
│       └── seed_user_activities.py
└── p2p-frontend-app/
    ├── README.md
    ├── components.json
    ├── eslint.config.js
    ├── index.html
    ├── package-lock.json
    ├── package.json
    ├── tsconfig.app.json
    ├── tsconfig.json
    ├── tsconfig.node.json
    ├── vite.config.ts
    ├── public/
    │   ├── Video_Redo_Realistic_Technology.mp4
    │   ├── logo.png
    │   └── vite.svg
    └── src/
        ├── App.css
        ├── App.tsx
        ├── index.css
        ├── main.tsx
        ├── vite-env.d.ts
        ├── assets/
        │   └── react.svg
        ├── components/
        │   ├── ImageUpload.tsx
        │   ├── InteractiveMap.tsx
        │   ├── LocationPicker.tsx
        │   ├── Navigation.tsx
        │   ├── ProtectedRoute.tsx
        │   ├── SaudiRiyal.tsx
        │   ├── SaudiRiyalTest.tsx
        │   ├── UseCasePopup.tsx
        │   ├── Auth/
        │   └── ui/
        │       ├── button.tsx
        │       ├── card.tsx
        │       ├── form.tsx
        │       ├── input.tsx
        │       ├── label.tsx
        │       ├── navigation-menu.tsx
        │       ├── select.tsx
        │       └── textarea.tsx
        ├── config/
        │   └── supertokens.ts
        ├── contexts/
        │   └── AuthContext.tsx
        ├── data/
        │   └── use-cases.json
        ├── lib/
        │   └── utils.ts
        ├── pages/
        │   ├── Dashboard.tsx
        │   ├── Forum.tsx
        │   ├── LandingPage.tsx
        │   ├── Login.tsx
        │   ├── Signup.tsx
        │   ├── SubmitUseCase.tsx
        │   ├── UseCaseDetail.tsx
        │   ├── UseCases.tsx
        │   └── UserManagement.tsx
        └── types/
            └── auth.ts
```

```
p2p-backend-app/
├── .env
├── alembic.ini
├── requirements.txt
├── use-cases.json
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── .gitkeep
│       ├── 5154fc59743b_initial_migration_create_users_user_.py
│       └── 8f5515e822b8_add_supertokens_id_field_to_users_table.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── dashboard.py
│   │           ├── forum.py
│   │           ├── health.py
│   │           ├── supertokens_auth.py
│   │           └── usecases.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── supertokens.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mongo_models.py
│   │   └── pg_models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── common.py
│   └── services/
│       ├── __init__.py
│       ├── database_service.py
│       └── user_activity_service.py
├── logs/
└── scripts/
    ├── __init__.py
    ├── init_db.py
    ├── seed_db_users.py
    ├── seed_forums.py
    ├── seed_usecases.py
    └── seed_user_activities.py
```

### Frontend Directory Structure (`p2p-frontend-app`)

```
p2p-frontend-app/
├── README.md
├── components.json
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── public/
│   ├── Video_Redo_Realistic_Technology.mp4
│   ├── logo.png
│   └── vite.svg
└── src/
    ├── App.css
    ├── App.tsx
    ├── index.css
    ├── main.tsx
    ├── vite-env.d.ts
    ├── assets/
    │   └── react.svg
    ├── components/
    │   ├── ImageUpload.tsx
    │   ├── InteractiveMap.tsx
    │   ├── LocationPicker.tsx
    │   ├── Navigation.tsx
    │   ├── ProtectedRoute.tsx
    │   ├── SaudiRiyal.tsx
    │   ├── SaudiRiyalTest.tsx
    │   ├── UseCasePopup.tsx
    │   ├── Auth/
    │   └── ui/
    │       ├── button.tsx
    │       ├── card.tsx
    │       ├── form.tsx
    │       ├── input.tsx
    │       ├── label.tsx
    │       ├── navigation-menu.tsx
    │       ├── select.tsx
    │       └── textarea.tsx
    ├── config/
    │   └── supertokens.ts
    ├── contexts/
    │   └── AuthContext.tsx
    ├── data/
    │   └── use-cases.json
    ├── lib/
    │   └── utils.ts
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Forum.tsx
    │   ├── LandingPage.tsx
    │   ├── Login.tsx
    │   ├── Signup.tsx
    │   ├── SubmitUseCase.tsx
    │   ├── UseCaseDetail.tsx
    │   ├── UseCases.tsx
    │   └── UserManagement.tsx
    └── types/
        └── auth.ts
```
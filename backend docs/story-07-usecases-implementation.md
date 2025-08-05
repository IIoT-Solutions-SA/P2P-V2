# Story 07: Use Cases Page Dynamic Data Implementation

## Overview

This story details the complete overhaul of the **Use Cases page**, transitioning it from a static proof-of-concept into a fully **dynamic, interactive, and database-driven feature**. All hardcoded data, including the list of use cases, categories, platform statistics, and top contributors, has been replaced with live data fetched from a series of new, robust API endpoints.

**Implementation Status:** ✅ **COMPLETED**
_All acceptance criteria have been successfully implemented, tested, and debugged._

---

## Acceptance Criteria

-   **✅ Use Cases Dynamic Data**
    -   [x] Replace hardcoded use case array with real data from `use-cases.json` and the database.
    -   [x] Replace hardcoded categories with dynamically generated categories based on real use case data, including accurate counts.
    -   [x] Replace hardcoded "Platform Stats" with real-time calculations from the database.
    -   [x] Replace hardcoded "Top Contributors" with a dynamic list based on the number of submitted use cases.
    -   [x] Implement category filtering that correctly queries and displays relevant use cases.
    -   [x] Implement sorting functionality (e.g., by "Most Viewed," "Most Liked").
    -   [x] Ensure all use cases display correct company names and industry data, not placeholder or incorrect user data.
    -   [x] Add loading states for all asynchronous data fetching to improve user experience.
    -   [x] Handle empty states gracefully when no use cases match a filter.

---

## Technical Implementation

### New API Endpoints Created

**Use Cases Endpoints (`/api/v1/use-cases/`)**

-   **`GET /`**: The main endpoint to fetch a list of use cases. It now supports query parameters for `category`, `search`, and `sort_by` to enable full filtering and sorting functionality.
-   **`GET /categories`**: Returns a list of all available use case categories, dynamically generated from the database with an accurate count of posts in each.
-   **`GET /stats`**: Returns key platform statistics, including total use cases, the number of unique contributing companies, and a count of featured success stories.
-   **`GET /contributors`**: Returns a ranked list of the top contributing companies based on the number of use cases they have submitted.

### Database Seeding Enhancements

The entire seeding process was modularized and made more robust to handle the complexity of the new dynamic features.

**User Seeding (`scripts/seed_db_users.py`)**
-   A dedicated script was created to handle user creation exclusively.
-   It now seeds users with a diverse set of `company` and `industry_sector` data that directly corresponds to the companies listed in `use-cases.json`, ensuring data integrity.

**Use Case Seeding (`scripts/seed_usecases.py`)**
-   This script now focuses solely on use cases, assuming users already exist.
-   It wipes all previous use cases to ensure a clean slate on every run.
-   It reads the `use-cases.json` file and creates 15 basic use cases, intelligently assigning a submitter by matching the `factoryName` to a user's company.
-   Crucially, it now populates each use case with randomized, realistic engagement data (views, likes, bookmarks) to make sorting features meaningful from the start.
-   It creates the 2 detailed enterprise use cases and correctly links them to their basic versions.

---

## Frontend Transformations

### Use Cases Page (`src/pages/UseCases.tsx`)

**Before (Hardcoded):**
```typescript
// Static fake data
const categories = [ { id: "all", name: "All Use Cases", count: 15 } ]
const useCases = [
  { id: 1, title: "AI Quality Inspection", company: "Fake Company" /* ... */ }
]
```

**After (Dynamic):**
```typescript
// Real API calls with states for filtering and sorting
const [categories, setCategories] = useState<Category[]>([]);
const [useCases, setUseCases] = useState<UseCase[]>([]);
const [selectedCategory, setSelectedCategory] = useState("all");
const [sortBy, setSortBy] = useState("newest");
const [loading, setLoading] = useState(true);

useEffect(() => {
  // Fetches categories, stats, and contributors
  fetchInitialData();
}, [user]);

useEffect(() => {
  // Fetches use cases whenever a filter or sort option changes
  fetchUseCases();
}, [user, selectedCategory, sortBy]);
```

---

## Critical Bug Fixes

-   **✅ Data Integrity and Display**
    -   **Issue:** The page was displaying the submitter's name as the "Company" and the category as the "Industry".
    -   **Solution:** The backend API (`usecases.py`) was corrected to map the correct database fields (`factory_name`, `industry_sector`) to the JSON response. The seeder was also updated to provide diverse industry data.

-   **✅ Seeder Script Failures**
    -   **Issue:** The seeder script was prone to `UnboundLocalError` if `use-cases.json` was not found and `ValidationError` due to missing required fields (`solution_description`, `location`).
    -   **Solution:** The script was refactored to initialize all variables at the top level. The data mapping logic was corrected to ensure all required fields defined in the Pydantic model are always included when creating a new `UseCase` document.

-   **✅ API Query Logic**
    -   **Issue:** The API was using an inefficient method to look up user data, making a separate database call for each use case. It also had a syntax error (`'ExpressionField' object is not callable`).
    -   **Solution:** The user lookup logic was optimized to fetch all required users in a single, efficient database query. The query syntax was corrected to use Beanie's `In` operator, resolving the runtime error.

---

## Performance Optimizations

### Efficient Database Queries

-   The `/categories`, `/stats`, and `/contributors` endpoints were rewritten to use **MongoDB's powerful aggregation pipeline**, which is significantly faster than fetching all documents and processing them in Python.
-   The main `/use-cases` endpoint now fetches all necessary user data in **one query** instead of N+1 queries.

### Frontend Loading States

-   The UI now displays a main loading spinner on initial page load.
-   A separate, smaller loading spinner is shown over the use case list when filters or sorting options are changed, providing a smooth user experience.
-   Empty states with user-friendly messages are displayed when no use cases match the selected criteria.

---

## Data Flow Architecture

> **Use Cases Page Data Flow**
> 
> `Page Load` → `Fetch Categories, Stats, Contributors` → `Fetch Initial Posts (sorted by newest)`
> 
> `User Clicks Filter` → `Refetch Posts with Category` → `Display Filtered Results`
> 
> `User Clicks Sort` → `Refetch Posts with Sort Param` → `Display Sorted Results`

---

## Testing Results

-   ✅ Category sidebar now displays correct categories with accurate post counts.
-   ✅ Filtering by any category correctly queries the API and displays only the relevant use cases.
-   ✅ The "All Use Cases" button correctly resets the filter and shows all posts.
-   ✅ Sorting by "Newest," "Most Viewed," and "Most Liked" works as expected.
-   ✅ All use cases display the correct Company Name, Industry, and Timeframe.
-   ✅ Loading spinners appear correctly during all data-fetching operations.
-   ✅ The "No use cases found" message appears when a filter results in an empty set.

---

## Conclusion

The Use Cases page is now a **fully featured, dynamic, and performant** part of the application. It successfully retrieves and displays all data from the backend, provides a robust filtering and sorting experience, and handles loading and empty states gracefully. The underlying data is now seeded correctly, ensuring a rich and realistic user experience from the first load.

### Key Achievements

-   **100% Dynamic Data:** All static arrays and objects have been eliminated.
-   **Full Interactivity:** Category filtering and engagement-based sorting are fully functional.
-   **Data Integrity:** The frontend now accurately reflects the structured data from the database.
-   **Robust Seeding:** The modularized seeding scripts ensure consistent and correct data population.
-   **Critical Bugs Resolved:** All identified backend and data mapping issues have been fixed.
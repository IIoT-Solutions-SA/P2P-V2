# Story 7: Search and Discovery Features

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 8  
**Priority**: High  
**Dependencies**: Story 1 (User Profiles), Story 2 (Forum System), Story 3 (Post Creation)

## User Story
**As a** platform user  
**I want** to search for relevant forum content, users, and expertise  
**So that** I can quickly find information, connect with experts, and discover solutions to my challenges

## Acceptance Criteria
- [ ] Full-text search across forum posts and replies with Arabic/English support
- [ ] Advanced filter options: category, tags, date range, user type, verification status
- [ ] User search with expertise, location, and industry filters
- [ ] Search suggestions and autocomplete for tags and topics
- [ ] Search result highlighting and snippet previews
- [ ] Recent searches and search history for logged-in users
- [ ] Bookmarking functionality for posts and search queries
- [ ] Search analytics and trending topics dashboard
- [ ] Mobile-optimized search interface with voice search
- [ ] Real-time search results with instant filtering

## Technical Specifications

### 1. Search Infrastructure

```python
# app/services/search_service.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re
from app.models.mongo_models import ForumPost, ForumReply, UserProfile
from app.schemas.search import SearchRequest, SearchResponse, SearchResult

class SearchService:
    @staticmethod
    async def search_content(
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20,
        user_id: Optional[str] = None
    ) -> SearchResponse:
        \"\"\"Comprehensive content search with filters\"\"\"
        
        # Normalize query for Arabic/English search
        normalized_query = SearchService._normalize_query(query)
        
        # Build search aggregation pipeline
        pipeline = SearchService._build_search_pipeline(
            normalized_query, filters, page, limit
        )
        
        # Execute search across posts and replies
        post_results = await SearchService._search_posts(pipeline)
        reply_results = await SearchService._search_replies(pipeline)
        
        # Combine and rank results
        combined_results = SearchService._combine_and_rank_results(
            post_results, reply_results, normalized_query
        )
        
        # Get total count for pagination
        total_count = await SearchService._get_search_count(normalized_query, filters)
        
        # Track search for analytics
        if user_id:
            await SearchService._track_search(user_id, query, filters)
        
        return SearchResponse(
            results=combined_results[:limit],
            total_count=total_count,
            page=page,
            limit=limit,
            query=query,
            filters=filters or {},
            search_time_ms=0  # Add timing
        )
    
    @staticmethod
    async def search_users(
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[UserProfile]:
        \"\"\"Search users by name, expertise, location\"\"\"
        
        search_filters = []
        
        # Text search across name, company, bio
        if query:
            text_search = {
                \"$or\": [
                    {\"name\": {\"$regex\": query, \"$options\": \"i\"}},
                    {\"company_name\": {\"$regex\": query, \"$options\": \"i\"}},
                    {\"bio\": {\"$regex\": query, \"$options\": \"i\"}}
                ]
            }
            search_filters.append(text_search)
        
        # Apply additional filters
        if filters:
            if filters.get('industry_sector'):
                search_filters.append({\"industry_sector\": filters['industry_sector']})
            
            if filters.get('location_city'):
                search_filters.append({\"location.city\": filters['location_city']})
            
            if filters.get('expertise_tags'):
                search_filters.append({
                    \"expertise_tags\": {\"$in\": filters['expertise_tags']}
                })
            
            if filters.get('verification_status'):
                search_filters.append({
                    \"verification_status\": filters['verification_status']
                })
            
            if filters.get('min_reputation'):
                search_filters.append({
                    \"reputation_score\": {\"$gte\": filters['min_reputation']}
                })
        
        # Only show public profiles
        search_filters.append({\"profile_visibility\": \"public\"})
        
        # Build final query
        final_query = {\"$and\": search_filters} if search_filters else {}
        
        # Execute search with sorting
        users = await UserProfile.find(final_query).sort([
            (\"verification_status\", -1),  # Verified users first
            (\"reputation_score\", -1),     # Then by reputation
            (\"last_activity_at\", -1)      # Then by activity
        ]).skip((page - 1) * limit).limit(limit).to_list()
        
        return users
    
    @staticmethod
    async def get_search_suggestions(query: str) -> List[str]:
        \"\"\"Get search suggestions based on query\"\"\"
        suggestions = []
        
        if len(query) >= 2:
            # Tag suggestions
            tag_suggestions = await SearchService._get_tag_suggestions(query)
            suggestions.extend(tag_suggestions)
            
            # Popular search suggestions
            popular_suggestions = await SearchService._get_popular_suggestions(query)
            suggestions.extend(popular_suggestions)
            
            # User/company suggestions
            user_suggestions = await SearchService._get_user_suggestions(query)
            suggestions.extend(user_suggestions)
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    @staticmethod
    async def get_trending_topics(days: int = 7) -> List[Dict[str, Any]]:
        \"\"\"Get trending topics based on search and post activity\"\"\"
        since = datetime.utcnow() - timedelta(days=days)
        
        # Aggregate trending tags from recent posts
        pipeline = [
            {\"$match\": {
                \"created_at\": {\"$gte\": since},
                \"status\": \"published\"
            }},
            {\"$unwind\": \"$tags\"},
            {\"$group\": {
                \"_id\": \"$tags\",
                \"count\": {\"$sum\": 1},
                \"recent_posts\": {\"$sum\": 1}
            }},
            {\"$sort\": {\"count\": -1}},
            {\"$limit\": 20}
        ]
        
        trending_tags = await ForumPost.aggregate(pipeline).to_list()
        
        return [
            {
                \"tag\": item[\"_id\"],
                \"post_count\": item[\"count\"],
                \"trend_score\": item[\"count\"]  # Could be more sophisticated
            }
            for item in trending_tags
        ]
    
    @staticmethod
    def _normalize_query(query: str) -> str:
        \"\"\"Normalize search query for better matching\"\"\"
        # Remove extra whitespace
        query = re.sub(r'\\s+', ' ', query.strip())
        
        # Handle Arabic text normalization
        # Add Arabic-specific normalization here
        
        return query
    
    @staticmethod
    def _build_search_pipeline(
        query: str, 
        filters: Optional[Dict[str, Any]], 
        page: int, 
        limit: int
    ) -> List[Dict[str, Any]]:
        \"\"\"Build MongoDB aggregation pipeline for search\"\"\"
        pipeline = []
        
        # Match stage
        match_conditions = []
        
        # Text search
        if query:
            text_conditions = {
                \"$or\": [
                    {\"title\": {\"$regex\": query, \"$options\": \"i\"}},
                    {\"content\": {\"$regex\": query, \"$options\": \"i\"}},
                    {\"tags\": {\"$in\": [query.lower()]}}
                ]
            }
            match_conditions.append(text_conditions)
        
        # Status filter
        match_conditions.append({\"status\": \"published\"})
        
        # Apply filters
        if filters:
            if filters.get('category_id'):
                match_conditions.append({\"category_id\": filters['category_id']})
            
            if filters.get('tags'):
                match_conditions.append({\"tags\": {\"$in\": filters['tags']}})
            
            if filters.get('date_from'):
                match_conditions.append({
                    \"created_at\": {\"$gte\": filters['date_from']}
                })
            
            if filters.get('date_to'):
                match_conditions.append({
                    \"created_at\": {\"$lte\": filters['date_to']}
                })
            
            if filters.get('has_best_answer'):
                match_conditions.append({\"has_best_answer\": True})
            
            if filters.get('verified_authors_only'):
                match_conditions.append({
                    \"author_verification_status\": \"verified\"
                })
        
        # Add match stage
        if match_conditions:
            pipeline.append({\"$match\": {\"$and\": match_conditions}})
        
        # Add scoring for relevance
        pipeline.extend([
            {
                \"$addFields\": {
                    \"relevance_score\": {
                        \"$add\": [
                            {\"$multiply\": [\"$view_count\", 0.1]},
                            {\"$multiply\": [\"$reply_count\", 2]},
                            {\"$multiply\": [\"$upvote_count\", 3]},
                            {\"$cond\": [\"$has_best_answer\", 10, 0]},
                            {\"$cond\": [\"$is_featured\", 20, 0]}
                        ]
                    }
                }
            },
            {\"$sort\": {
                \"relevance_score\": -1,
                \"created_at\": -1
            }},
            {\"$skip\": (page - 1) * limit},
            {\"$limit\": limit}
        ])
        
        return pipeline

# Search tracking model
class SearchHistory(Document):
    user_id: str
    query: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    results_count: int
    clicked_result_id: Optional[str] = None
    search_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = \"search_history\"
        indexes = [
            [(\"user_id\", pymongo.ASCENDING)],
            [(\"search_timestamp\", pymongo.DESCENDING)],
            [(\"query\", pymongo.TEXT)]
        ]
```

### 2. Search API Endpoints

```python
# app/api/v1/endpoints/search.py
@router.post(\"/content\", response_model=SearchResponse)
async def search_content(
    search_request: SearchRequest,
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    \"\"\"Search forum content with filters\"\"\"
    user_id = session.get_user_id() if session else None
    
    try:
        results = await SearchService.search_content(
            query=search_request.query,
            filters=search_request.filters,
            page=search_request.page,
            limit=search_request.limit,
            user_id=user_id
        )
        return results
    except Exception as e:
        logger.error(f\"Content search failed: {e}\")
        raise HTTPException(status_code=500, detail=\"Search failed\")

@router.post(\"/users\", response_model=List[UserSearchResult])
async def search_users(
    search_request: UserSearchRequest
):
    \"\"\"Search users by expertise and location\"\"\"
    try:
        users = await SearchService.search_users(
            query=search_request.query,
            filters=search_request.filters,
            page=search_request.page,
            limit=search_request.limit
        )
        return [UserSearchResult.from_profile(user) for user in users]
    except Exception as e:
        logger.error(f\"User search failed: {e}\")
        raise HTTPException(status_code=500, detail=\"User search failed\")

@router.get(\"/suggestions\")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description=\"Search query for suggestions\")
):
    \"\"\"Get search suggestions\"\"\"
    try:
        suggestions = await SearchService.get_search_suggestions(q)
        return {\"suggestions\": suggestions}
    except Exception as e:
        logger.error(f\"Suggestions failed: {e}\")
        raise HTTPException(status_code=500, detail=\"Failed to get suggestions\")

@router.get(\"/trending\")
async def get_trending_topics(
    days: int = Query(7, ge=1, le=30, description=\"Days to look back for trends\")
):
    \"\"\"Get trending topics\"\"\"
    try:
        trending = await SearchService.get_trending_topics(days)
        return {\"trending_topics\": trending}
    except Exception as e:
        logger.error(f\"Trending topics failed: {e}\")
        raise HTTPException(status_code=500, detail=\"Failed to get trending topics\")

@router.get(\"/history\")
async def get_search_history(
    limit: int = Query(20, ge=1, le=50),
    session: SessionContainer = Depends(verify_session())
):
    \"\"\"Get user's search history\"\"\"
    user_id = session.get_user_id()
    
    try:
        history = await SearchHistory.find(
            SearchHistory.user_id == user_id
        ).sort([(\"search_timestamp\", -1)]).limit(limit).to_list()
        
        return {
            \"history\": [
                {
                    \"query\": item.query,
                    \"timestamp\": item.search_timestamp,
                    \"results_count\": item.results_count
                }
                for item in history
            ]
        }
    except Exception as e:
        logger.error(f\"Search history failed: {e}\")
        raise HTTPException(status_code=500, detail=\"Failed to get search history\")
```

### 3. Frontend Search Components

```typescript
// SearchInterface.tsx
import { useState, useEffect, useCallback } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { Search, Filter, Trending, History } from 'lucide-react';

interface SearchInterfaceProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  loading?: boolean;
}

export default function SearchInterface({ onSearch, loading }: SearchInterfaceProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  
  const debouncedQuery = useDebounce(query, 300);
  
  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      fetchSuggestions(debouncedQuery);
    } else {
      setSuggestions([]);
    }
  }, [debouncedQuery]);
  
  const fetchSuggestions = async (searchQuery: string) => {
    try {
      const response = await api.get(`/api/v1/search/suggestions?q=${encodeURIComponent(searchQuery)}`);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };
  
  const handleSearch = useCallback(() => {
    if (query.trim()) {
      onSearch(query, filters);
      setShowSuggestions(false);
    }
  }, [query, filters, onSearch]);
  
  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    onSearch(suggestion, filters);
    setShowSuggestions(false);
  };
  
  return (
    <div className=\"w-full max-w-4xl mx-auto\">
      {/* Main Search Bar */}
      <div className=\"relative\">
        <div className=\"flex items-center\">
          <div className=\"relative flex-1\">
            <Search className=\"absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400\" />
            <Input
              type=\"text\"
              placeholder={t('search.placeholder')}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className=\"pl-10 pr-4 py-3 text-lg\"
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            />
            
            {/* Search Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
              <div className=\"absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg\">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    className=\"w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center\"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <Search className=\"h-3 w-3 mr-2 text-gray-400\" />
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <Button 
            onClick={handleSearch} 
            disabled={!query.trim() || loading}
            className=\"ml-2\"
          >
            {loading ? t('common.searching') : t('search.search')}
          </Button>
          
          <Button
            variant=\"outline\"
            onClick={() => setShowFilters(!showFilters)}
            className=\"ml-2\"
          >
            <Filter className=\"h-4 w-4\" />
          </Button>
        </div>
        
        {/* Advanced Filters */}
        {showFilters && (
          <Card className=\"mt-4 p-4\">
            <SearchFilters 
              filters={filters} 
              onChange={setFilters}
              onApply={() => setShowFilters(false)}
            />
          </Card>
        )}
      </div>
      
      {/* Quick Actions */}
      <div className=\"flex items-center space-x-4 mt-4\">
        <TrendingTopics onTopicClick={handleSuggestionClick} />
        <SearchHistory onHistoryClick={handleSuggestionClick} />
      </div>
    </div>
  );
}

// SearchResults.tsx
interface SearchResultsProps {
  results: SearchResult[];
  totalCount: number;
  query: string;
  loading: boolean;
  onLoadMore: () => void;
}

export function SearchResults({ results, totalCount, query, loading, onLoadMore }: SearchResultsProps) {
  const { t } = useTranslation();
  
  if (loading && results.length === 0) {
    return <SearchSkeleton />;
  }
  
  if (!loading && results.length === 0 && query) {
    return (
      <div className=\"text-center py-12\">
        <Search className=\"h-12 w-12 text-gray-400 mx-auto mb-4\" />
        <h3 className=\"text-lg font-medium text-gray-900 mb-2\">
          {t('search.no_results')}
        </h3>
        <p className=\"text-gray-600\">
          {t('search.try_different_terms')}
        </p>
      </div>
    );
  }
  
  return (
    <div className=\"space-y-6\">
      {/* Results Summary */}
      <div className=\"flex justify-between items-center\">
        <p className=\"text-sm text-gray-600\">
          {t('search.results_count', { count: totalCount, query })}
        </p>
        <SearchSortDropdown />
      </div>
      
      {/* Results List */}
      <div className=\"space-y-4\">
        {results.map((result) => (
          <SearchResultCard key={result.id} result={result} />
        ))}
      </div>
      
      {/* Load More */}
      {results.length < totalCount && (
        <div className=\"text-center\">
          <Button 
            variant=\"outline\" 
            onClick={onLoadMore}
            disabled={loading}
          >
            {loading ? t('common.loading') : t('search.load_more')}
          </Button>
        </div>
      )}
    </div>
  );
}
```

### 4. Search Schemas

```python
# app/schemas/search.py
class SearchFilters(BaseModel):
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    has_best_answer: Optional[bool] = None
    verified_authors_only: Optional[bool] = None
    min_upvotes: Optional[int] = None

class SearchRequest(BaseModel):
    query: str
    filters: SearchFilters = SearchFilters()
    page: int = 1
    limit: int = 20
    sort_by: str = \"relevance\"  # relevance, date, popularity

class SearchResult(BaseModel):
    id: str
    type: str  # post, reply, user
    title: str
    content_snippet: str
    author: Dict[str, str]
    category: Optional[Dict[str, str]]
    tags: List[str]
    created_at: datetime
    relevance_score: float
    highlight: Optional[str] = None  # Highlighted search terms

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int
    page: int
    limit: int
    query: str
    filters: SearchFilters
    search_time_ms: int
    suggestions: List[str] = []
```

## Implementation Steps

1. **Search Infrastructure**
   - Set up MongoDB text indexes
   - Implement search aggregation pipelines
   - Add search result ranking algorithms

2. **API Development**
   - Create search endpoints with filtering
   - Implement suggestion and autocomplete
   - Add search analytics tracking

3. **Frontend Interface**
   - Build responsive search interface
   - Implement real-time search suggestions
   - Add advanced filtering options

4. **Performance Optimization**
   - Index optimization for search queries
   - Result caching for popular searches
   - Search result pagination

## Testing Checklist
- [ ] Full-text search works across posts and replies
- [ ] Arabic text search functions correctly
- [ ] Advanced filters produce accurate results
- [ ] Search suggestions are relevant and fast
- [ ] User search finds correct profiles
- [ ] Search performance is acceptable (<500ms)
- [ ] Mobile search interface is responsive
- [ ] Search analytics track user behavior
- [ ] Trending topics update correctly
- [ ] Search history saves and displays properly

## Performance Considerations
- [ ] Database indexes optimized for search queries
- [ ] Search result caching implemented
- [ ] Query optimization for large datasets
- [ ] Real-time suggestion performance
- [ ] Search analytics without performance impact

## Dependencies
- Story 1 (User Profiles) completed
- Story 2 (Forum System) completed
- Story 3 (Post Creation) completed
- Database indexing configured

## Notes
- Consider Elasticsearch integration for advanced search
- Implement search result click tracking
- Plan for multilingual search expansion
- Add voice search functionality for mobile
- Consider AI-powered search improvements
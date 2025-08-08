"""Performance optimization service for caching and query optimization."""

from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timedelta
import asyncio
import json
import hashlib
from functools import wraps
from uuid import UUID

from app.core.logging import get_logger

logger = get_logger(__name__)
from app.models.dashboard import PerformanceMetrics


class CacheService:
    """In-memory cache service for performance optimization."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
        self._max_cache_size = 1000  # Maximum number of cache entries
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if entry['expires_at'] > datetime.utcnow():
                self._cache_stats['hits'] += 1
                # Move to end (LRU)
                self._cache[key] = self._cache.pop(key)
                return entry['value']
            else:
                # Expired entry
                del self._cache[key]
        
        self._cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL."""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # Check if we need to evict entries
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entry (LRU)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._cache_stats['evictions'] += 1
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
        self._cache_stats['sets'] += 1
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._cache_stats,
            'total_requests': total_requests,
            'hit_rate_percentage': round(hit_rate, 2),
            'current_size': len(self._cache),
            'max_size': self._max_cache_size
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry['expires_at'] <= now
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)


# Global cache instance
cache_service = CacheService()


def cache_result(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func.__name__, key_prefix, args, kwargs)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_service.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cache set for key: {cache_key}")
            
            return result
        return wrapper
    return decorator


def _generate_cache_key(func_name: str, prefix: str, args: tuple, kwargs: dict) -> str:
    """Generate cache key from function name and arguments."""
    # Convert args and kwargs to a hashable string
    args_str = str(args) + str(sorted(kwargs.items()))
    key_hash = hashlib.md5(args_str.encode()).hexdigest()
    
    return f"{prefix}:{func_name}:{key_hash}"


class PerformanceService:
    """Service for performance monitoring and optimization."""
    
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'db_queries': 0,
            'cache_operations': 0,
            'response_times': [],
            'errors': 0
        }
        self.start_time = datetime.utcnow()
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        cache_stats = cache_service.get_stats()
        
        # Calculate average response time
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        # Calculate error rate
        total_requests = self.metrics['api_calls']
        error_rate = (self.metrics['errors'] / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        return PerformanceMetrics(
            api_metrics={
                'total_calls': self.metrics['api_calls'],
                'average_response_time_ms': round(avg_response_time, 2),
                'error_rate_percentage': round(error_rate, 2),
                'requests_per_second': round(total_requests / max(uptime_seconds, 1), 2)
            },
            database_metrics={
                'total_queries': self.metrics['db_queries'],
                'queries_per_second': round(self.metrics['db_queries'] / max(uptime_seconds, 1), 2)
            },
            cache_metrics={
                'hit_rate_percentage': cache_stats['hit_rate_percentage'],
                'total_operations': cache_stats['total_requests'],
                'current_size': cache_stats['current_size'],
                'evictions': cache_stats['evictions']
            },
            error_metrics={
                'total_errors': self.metrics['errors'],
                'error_rate_percentage': round(error_rate, 2)
            },
            resource_usage={
                'uptime_seconds': round(uptime_seconds, 2),
                'memory_usage_mb': 0,  # Would need psutil for actual memory usage
                'cpu_usage_percentage': 0  # Would need psutil for actual CPU usage
            }
        )
    
    def record_api_call(self, response_time_ms: float) -> None:
        """Record an API call."""
        self.metrics['api_calls'] += 1
        self.metrics['response_times'].append(response_time_ms)
        
        # Keep only last 1000 response times to prevent memory growth
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_db_query(self) -> None:
        """Record a database query."""
        self.metrics['db_queries'] += 1
    
    def record_error(self) -> None:
        """Record an error."""
        self.metrics['errors'] += 1
    
    async def optimize_database_queries(self) -> Dict[str, Any]:
        """Suggest database query optimizations."""
        # This would analyze slow query logs and suggest indexes
        recommendations = []
        
        # Mock recommendations based on common patterns
        recommendations.append({
            'type': 'index',
            'table': 'forum_posts',
            'columns': ['created_at', 'is_deleted'],
            'reason': 'Frequently used in ORDER BY with WHERE clause'
        })
        
        recommendations.append({
            'type': 'index',
            'table': 'users',
            'columns': ['organization_id', 'last_active'],
            'reason': 'Common filter combination for active users query'
        })
        
        recommendations.append({
            'type': 'query_optimization',
            'description': 'Use LIMIT in subqueries before JOINs',
            'impact': 'Reduce memory usage and improve performance'
        })
        
        return {
            'recommendations': recommendations,
            'analyzed_at': datetime.utcnow().isoformat(),
            'total_queries_analyzed': self.metrics['db_queries']
        }
    
    async def clean_cache(self) -> Dict[str, Any]:
        """Clean expired cache entries."""
        expired_count = cache_service.cleanup_expired()
        
        return {
            'expired_entries_removed': expired_count,
            'current_cache_size': len(cache_service._cache),
            'cache_stats': cache_service.get_stats()
        }
    
    async def get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get list of slow queries (mock implementation)."""
        # In production, this would query PostgreSQL's pg_stat_statements
        mock_slow_queries = [
            {
                'query': 'SELECT * FROM forum_posts JOIN users ON ...',
                'avg_time_ms': 250.5,
                'call_count': 1250,
                'total_time_ms': 313125,
                'suggestion': 'Add composite index on (topic_id, created_at)'
            },
            {
                'query': 'SELECT COUNT(*) FROM use_cases WHERE ...',
                'avg_time_ms': 180.2,
                'call_count': 890,
                'total_time_ms': 160378,
                'suggestion': 'Add partial index on status column'
            }
        ]
        
        return mock_slow_queries
    
    def reset_metrics(self) -> None:
        """Reset performance metrics."""
        self.metrics = {
            'api_calls': 0,
            'db_queries': 0,
            'cache_operations': 0,
            'response_times': [],
            'errors': 0
        }
        self.start_time = datetime.utcnow()


# Global performance service instance
performance_service = PerformanceService()


class DatabaseOptimizer:
    """Database query optimization utilities."""
    
    @staticmethod
    def get_recommended_indexes() -> List[Dict[str, Any]]:
        """Get recommended database indexes."""
        return [
            {
                'table': 'forum_posts',
                'index': 'idx_forum_posts_topic_created',
                'columns': ['topic_id', 'created_at'],
                'type': 'btree',
                'reason': 'Optimize topic post listing with chronological order'
            },
            {
                'table': 'forum_posts',
                'index': 'idx_forum_posts_author_active',
                'columns': ['author_id', 'is_deleted'],
                'type': 'btree',
                'reason': 'Optimize user post history queries'
            },
            {
                'table': 'messages',
                'index': 'idx_messages_conversation_created',
                'columns': ['conversation_id', 'created_at'],
                'type': 'btree',
                'reason': 'Optimize message retrieval by conversation'
            },
            {
                'table': 'messages',
                'index': 'idx_messages_recipient_unread',
                'columns': ['recipient_id', 'is_read'],
                'type': 'btree',
                'reason': 'Optimize unread message queries'
            },
            {
                'table': 'notifications',
                'index': 'idx_notifications_user_read',
                'columns': ['user_id', 'is_read', 'created_at'],
                'type': 'btree',
                'reason': 'Optimize notification feed queries'
            },
            {
                'table': 'users',
                'index': 'idx_users_org_active',
                'columns': ['organization_id', 'last_active'],
                'type': 'btree',
                'reason': 'Optimize active users statistics'
            }
        ]
    
    @staticmethod
    def get_query_optimization_tips() -> List[Dict[str, str]]:
        """Get query optimization tips."""
        return [
            {
                'tip': 'Use LIMIT with ORDER BY',
                'description': 'Always use LIMIT when you don\'t need all results to prevent full table scans'
            },
            {
                'tip': 'Filter before JOIN',
                'description': 'Apply WHERE conditions before JOINs to reduce the dataset size'
            },
            {
                'tip': 'Use EXISTS instead of IN',
                'description': 'EXISTS can be more efficient than IN for correlated subqueries'
            },
            {
                'tip': 'Avoid SELECT *',
                'description': 'Only select the columns you need to reduce data transfer'
            },
            {
                'tip': 'Use partial indexes',
                'description': 'Create indexes with WHERE conditions for frequently filtered queries'
            }
        ]
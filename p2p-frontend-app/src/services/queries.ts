/**
 * TanStack Query Hooks and Configuration
 * Centralized data fetching logic using React Query
 */
import { QueryClient } from '@tanstack/react-query';
import { healthCheck } from './api';

// Create and configure the query client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    },
    mutations: {
      retry: 1,
    },
  },
});

// Query keys for consistent cache management
export const queryKeys = {
  health: ['health'] as const,
  // TODO: Add more query keys as we implement features
  // users: ['users'] as const,
  // forums: ['forums'] as const,
  // useCases: ['useCases'] as const,
};

// Health check query hook
export const useHealthCheck = () => {
  return {
    queryKey: queryKeys.health,
    queryFn: healthCheck,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 3,
  };
};

// TODO: Add more query hooks as we implement features
// Example structure for future queries:
/*
export const useUsers = () => {
  return {
    queryKey: queryKeys.users,
    queryFn: () => userService.getUsers(),
  };
};

export const useForums = () => {
  return {
    queryKey: queryKeys.forums,
    queryFn: () => forumService.getForums(),
  };
};
*/
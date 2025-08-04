/**
 * API Types
 * Shared type definitions for API responses and requests
 */

// Common API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  timestamp: string;
}

// Error response structure
export interface ApiError {
  error: string;
  message: string;
  statusCode: number;
  timestamp: string;
  path?: string;
}

// Health check response (matches backend)
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  checks: {
    api: 'operational' | 'down';
    database?: 'operational' | 'down';
    redis?: 'operational' | 'down';
    supertokens?: 'operational' | 'down';
  };
}

// Pagination metadata
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Paginated response wrapper
export interface PaginatedResponse<T> {
  data: T[];
  meta: PaginationMeta;
}

// Query parameters for API requests
export interface QueryParams {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  [key: string]: any;
}

// File upload response
export interface FileUploadResponse {
  url: string;
  filename: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
}
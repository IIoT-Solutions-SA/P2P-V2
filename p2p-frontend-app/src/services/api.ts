/**
 * API Service Layer with SuperTokens Integration
 * Central configuration for all backend API calls with session management
 */
import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import Session from 'supertokens-auth-react/recipe/session';

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default configuration
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for SuperTokens cookies
});

// Add SuperTokens interceptors
Session.addAxiosInterceptors(apiClient);

// Request interceptor for additional headers or logging
apiClient.interceptors.request.use(
  (config) => {
    // Log the request in development
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log successful response in development
    if (import.meta.env.DEV) {
      console.log(`API Response: ${response.config.url} - Status: ${response.status}`);
    }
    return response;
  },
  async (error) => {
    // Handle common HTTP errors
    if (error.response?.status === 401) {
      // SuperTokens will handle 401 automatically via its interceptor
      // This will attempt to refresh the session
      console.warn('Unauthorized access - session may have expired');
      
      // Check if this is NOT an auth endpoint
      if (!error.config.url?.includes('/auth/')) {
        // Session expired and couldn't be refreshed
        // Redirect to login
        if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    } else if (error.response?.status === 403) {
      console.warn('Forbidden access - insufficient permissions');
      // Handle forbidden access (e.g., show error message)
    } else if (error.response?.status === 404) {
      console.warn('Resource not found');
    } else if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data);
    }
    
    return Promise.reject(error);
  }
);

// Generic API methods
export const api = {
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.get<T>(url, config),
  
  post: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.post<T>(url, data, config),
  
  put: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.put<T>(url, data, config),
  
  patch: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.patch<T>(url, data, config),
  
  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.delete<T>(url, config),
  
  // File upload with proper content type
  upload: <T>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> =>
    apiClient.post<T>(url, formData, {
      ...config,
      headers: {
        ...config?.headers,
        'Content-Type': 'multipart/form-data',
      },
    }),
};

// Health check function for testing backend connection
export const healthCheck = async (): Promise<{ status: string; service: string; checks: object }> => {
  try {
    const response = await api.get<{ status: string; service: string; checks: object }>('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// Auth-specific API endpoints
export const authApi = {
  // These will be handled by SuperTokens, but we keep them for reference
  login: async (email: string, password: string) => {
    return api.post('/auth/signin', { 
      formFields: [
        { id: 'email', value: email },
        { id: 'password', value: password }
      ]
    });
  },
  
  signup: async (data: any) => {
    return api.post('/auth/signup', data);
  },
  
  logout: async () => {
    return api.post('/auth/signout');
  },
  
  // Custom endpoints
  getCurrentUser: async () => {
    return api.get('/api/v1/users/me');
  },
  
  updateProfile: async (data: any) => {
    return api.patch('/api/v1/users/me', data);
  },
};

// Organization-specific API endpoints
export const organizationApi = {
  getCurrent: async () => {
    return api.get('/api/v1/organizations/me');
  },
  
  update: async (data: any) => {
    return api.patch('/api/v1/organizations/me', data);
  },
  
  getStats: async () => {
    return api.get('/api/v1/organizations/stats');
  },
  
  uploadLogo: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload('/api/v1/organizations/me/logo', formData);
  },
};

// User management API endpoints
export const userApi = {
  list: async (params?: { page?: number; pageSize?: number; search?: string }) => {
    return api.get('/api/v1/users/organization', { params });
  },
  
  getById: async (id: string) => {
    return api.get(`/api/v1/users/${id}`);
  },
  
  updateById: async (id: string, data: any) => {
    return api.patch(`/api/v1/users/${id}`, data);
  },
  
  deleteById: async (id: string) => {
    return api.delete(`/api/v1/users/${id}`);
  },
  
  inviteUser: async (email: string, role: string) => {
    return api.post('/api/v1/invitations/send', { email, role });
  },
};

export default api;
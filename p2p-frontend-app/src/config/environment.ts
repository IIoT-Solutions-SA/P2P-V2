// Environment configuration for API base URL
// DEFAULT: Production (uses IP address 15.185.167.236)
// Development: Set NODE_ENV=development to use localhost

export const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  : import.meta.env.VITE_API_BASE_URL || 'http://15.185.167.236:8000';

export const WEBSITE_BASE_URL = process.env.NODE_ENV === 'development'
  ? import.meta.env.VITE_WEBSITE_BASE_URL || 'http://localhost:5173'
  : import.meta.env.VITE_WEBSITE_BASE_URL || 'http://15.185.167.236:5173';

// Helper function to build API URLs
export const buildApiUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

// Helper function to build full URLs
export const buildWebsiteUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${WEBSITE_BASE_URL}${cleanPath}`;
};

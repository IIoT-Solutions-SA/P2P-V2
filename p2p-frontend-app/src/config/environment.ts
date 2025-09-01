// Environment configuration for API base URL
// DEFAULT: Development (uses localhost)
// Production: Set VITE_NODE_ENV=production to use production server

export const API_BASE_URL = import.meta.env.VITE_NODE_ENV === 'production' 
  ? import.meta.env.VITE_API_BASE_URL || 'http://15.185.167.236:8000'
  : import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const WEBSITE_BASE_URL = import.meta.env.VITE_NODE_ENV === 'production'
  ? import.meta.env.VITE_WEBSITE_BASE_URL || 'http://15.185.167.236:5173'
  : import.meta.env.VITE_WEBSITE_BASE_URL || 'http://localhost:5173';

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

// Environment configuration for API base URL
// Smart environment detection based on hostname - automatically determines if running locally or on production server

// Smart environment detection based on hostname
const isProductionServer = window.location.hostname === 'peerlink.c4ir.sa';

const isForcedProduction = import.meta.env.VITE_NODE_ENV === 'production';

export const IS_DEV_ENV = !isForcedProduction && (
  import.meta.env.MODE === 'development' ||
  import.meta.env.VITE_ENVIRONMENT === 'development' ||
  import.meta.env.VITE_NODE_ENV === 'development'
);

// Use environment variables if set, otherwise use smart detection based on hostname
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isProductionServer ? 'https://peerlink.c4ir.sa' : 'http://localhost:8000');

export const WEBSITE_BASE_URL = import.meta.env.VITE_WEBSITE_BASE_URL ||
  (isProductionServer ? 'https://peerlink.c4ir.sa' : 'http://localhost:5173');

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

// Alias for backward compatibility
export const getApiUrl = (): string => API_BASE_URL;

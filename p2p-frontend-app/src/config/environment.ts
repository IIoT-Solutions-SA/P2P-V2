// Environment configuration for API base URL
// Smart environment detection based on hostname - automatically determines if running locally or on production server

// Smart environment detection based on hostname
const isProductionServer = window.location.hostname === '15.185.167.236';

// Use environment variables if set, otherwise use smart detection based on hostname
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isProductionServer ? 'http://15.185.167.236:8000' : 'http://localhost:8000');

export const WEBSITE_BASE_URL = import.meta.env.VITE_WEBSITE_BASE_URL ||
  (isProductionServer ? 'http://15.185.167.236:5173' : 'http://localhost:5173');

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

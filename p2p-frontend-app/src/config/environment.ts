// Environment configuration for API base URL
// Smart environment detection based on hostname - automatically determines if running locally or on production server
const PRODUCTION_HOSTS = new Set([
  'peerlink.c4ir.sa',
  'p2p.iiotsolutions.sa',
  '145.241.154.18',
])
const isProductionServer = PRODUCTION_HOSTS.has(window.location.hostname)
const isRemoteAccess = !['localhost', '127.0.0.1', '0.0.0.0'].includes(window.location.hostname)
const currentOrigin = window.location.origin
const isForcedProduction = import.meta.env.VITE_NODE_ENV === 'production'
export const IS_DEV_ENV = !isForcedProduction && (
  import.meta.env.MODE === 'development' ||
  import.meta.env.VITE_ENVIRONMENT === 'development' ||
  import.meta.env.VITE_NODE_ENV === 'development'
)
// Vite's source-development server talks directly to the backend on port 8000.
// Every built/deployed copy (including the Android-emulator PWA tunnel) must stay
// same-origin so nginx can proxy /api and /auth without exposing a second port.
const developmentApiOrigin = `${window.location.protocol}//${window.location.hostname}:8000`
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV && !isProductionServer && !isRemoteAccess ? developmentApiOrigin : currentOrigin)
export const WEBSITE_BASE_URL = import.meta.env.VITE_WEBSITE_BASE_URL || currentOrigin
// Helper function to build API URLs
export const buildApiUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${cleanPath}`
}
// Helper function to build full URLs
export const buildWebsiteUrl = (path: string): string => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${WEBSITE_BASE_URL}${cleanPath}`
}
// Alias for backward compatibility
export const getApiUrl = (): string => API_BASE_URL

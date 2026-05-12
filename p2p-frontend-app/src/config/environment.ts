// Environment configuration for API base URL
// Smart environment detection based on hostname - automatically determines if running locally or on production server
const PRODUCTION_HOSTS = new Set([
  'peerlink.c4ir.sa',
  'p2p.iiotsolutions.sa',
  '145.241.154.18',
])
const isProductionServer = PRODUCTION_HOSTS.has(window.location.hostname)
const currentOrigin = window.location.origin
const isForcedProduction = import.meta.env.VITE_NODE_ENV === 'production'
export const IS_DEV_ENV = !isForcedProduction && (
  import.meta.env.MODE === 'development' ||
  import.meta.env.VITE_ENVIRONMENT === 'development' ||
  import.meta.env.VITE_NODE_ENV === 'development'
)
// Use environment variables if set, otherwise use current origin for deployed environments.
// nginx proxies /api and /auth on the same host, so same-origin is the safest production default.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isProductionServer ? currentOrigin : 'http://localhost:8000')
export const WEBSITE_BASE_URL = import.meta.env.VITE_WEBSITE_BASE_URL ||
  (isProductionServer ? currentOrigin : 'http://localhost:5173')
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

const CACHE_VERSION = 'peerlink-pwa-v3'
const APP_SHELL = [
  '/',
  '/manifest.webmanifest',
  '/logo.svg',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-512.png',
]

const offlineResponse = () => new Response('PeerLink is temporarily offline.', {
  status: 503,
  headers: { 'Content-Type': 'text/plain; charset=utf-8' },
})

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_VERSION).then((cache) => cache.addAll(APP_SHELL)))
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_VERSION).map((key) => caches.delete(key)),
    )),
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  const url = new URL(request.url)

  if (request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request)
        if (response.ok) {
          const cache = await caches.open(CACHE_VERSION)
          await cache.put('/', response.clone())
        }
        return response
      } catch {
        return (await caches.match('/')) || offlineResponse()
      }
    })())
    return
  }

  const networkResponse = fetch(request)
    .then(async (response) => {
      if (response.ok) {
        const cache = await caches.open(CACHE_VERSION)
        await cache.put(request, response.clone())
      }
      return response
    })
    .catch(() => null)

  event.waitUntil(networkResponse.then(() => undefined))
  event.respondWith(
    caches.match(request).then(async (cached) => cached || (await networkResponse) || offlineResponse()),
  )
})

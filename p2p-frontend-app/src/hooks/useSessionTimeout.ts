import { useEffect, useRef } from 'react'

const DEFAULT_IDLE_TIMEOUT_MINUTES = 30
const ACTIVITY_WRITE_THROTTLE_MS = 15_000
const ACTIVITY_HEARTBEAT_INTERVAL_MS = 60_000
const CHECK_INTERVAL_MS = 10_000
const LAST_ACTIVITY_KEY = 'peerlink.session.lastActivityAt'

const configuredMinutes = Number(import.meta.env.VITE_SESSION_IDLE_TIMEOUT_MINUTES)
const acceptanceSeconds = Number(import.meta.env.VITE_SESSION_IDLE_TIMEOUT_SECONDS_TEST)
const isAcceptanceTest = import.meta.env.MODE === 'test'
export const SESSION_IDLE_TIMEOUT_MS =
  isAcceptanceTest && Number.isFinite(acceptanceSeconds) && acceptanceSeconds > 0
    ? acceptanceSeconds * 1_000
    : (Number.isFinite(configuredMinutes) && configuredMinutes > 0
        ? configuredMinutes
        : DEFAULT_IDLE_TIMEOUT_MINUTES) * 60_000

/**
 * Signs an authenticated user out after genuine browser inactivity.
 *
 * The timestamp is shared through localStorage so activity and expiry remain
 * consistent across PeerLink tabs. The backend independently enforces the same
 * idle limit and the eight-hour absolute lifetime; this hook provides timely UX
 * without weakening server-side enforcement.
 */
export function useSessionTimeout(
  isAuthenticated: boolean,
  onTimeout: () => Promise<void>,
  onActivity: () => Promise<unknown>,
) {
  const timingOut = useRef(false)
  const lastWrite = useRef(0)
  const lastHeartbeat = useRef(0)
  const timeoutCallback = useRef(onTimeout)
  const activityCallback = useRef(onActivity)
  timeoutCallback.current = onTimeout
  activityCallback.current = onActivity

  useEffect(() => {
    if (!isAuthenticated) {
      timingOut.current = false
      return
    }

    const triggerTimeout = () => {
      if (timingOut.current) return
      timingOut.current = true
      localStorage.removeItem(LAST_ACTIVITY_KEY)
      void timeoutCallback.current().finally(() => {
        timingOut.current = false
      })
    }

    const recordActivity = () => {
      const now = Date.now()
      if (now - lastWrite.current < ACTIVITY_WRITE_THROTTLE_MS) return
      lastWrite.current = now
      localStorage.setItem(LAST_ACTIVITY_KEY, String(now))

      // Scrolls and other local-only interactions may not otherwise call the API.
      // This authenticated heartbeat keeps backend idle state aligned with real
      // browser activity while remaining limited to one request per minute.
      if (now - lastHeartbeat.current >= ACTIVITY_HEARTBEAT_INTERVAL_MS) {
        lastHeartbeat.current = now
        void activityCallback.current().catch(triggerTimeout)
      }
    }

    const expireIfIdle = () => {
      if (timingOut.current) return
      const stored = Number(localStorage.getItem(LAST_ACTIVITY_KEY))
      const lastActivity = Number.isFinite(stored) && stored > 0 ? stored : Date.now()
      if (Date.now() - lastActivity < SESSION_IDLE_TIMEOUT_MS) return
      triggerTimeout()
    }

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        expireIfIdle()
        if (!timingOut.current) recordActivity()
      }
    }

    const handleStorage = (event: StorageEvent) => {
      if (event.key !== LAST_ACTIVITY_KEY) return
      // Removal is the expiry signal emitted by another PeerLink tab.
      if (event.newValue === null && event.oldValue !== null) {
        triggerTimeout()
        return
      }
      expireIfIdle()
    }

    // Loading or returning to the application is user activity.
    recordActivity()
    const activityEvents: Array<keyof WindowEventMap> = [
      'pointerdown',
      'keydown',
      'scroll',
      'touchstart',
    ]
    activityEvents.forEach((eventName) =>
      window.addEventListener(eventName, recordActivity, { passive: true }),
    )
    document.addEventListener('visibilitychange', handleVisibility)
    window.addEventListener('storage', handleStorage)
    const interval = window.setInterval(expireIfIdle, CHECK_INTERVAL_MS)

    return () => {
      activityEvents.forEach((eventName) =>
        window.removeEventListener(eventName, recordActivity),
      )
      document.removeEventListener('visibilitychange', handleVisibility)
      window.removeEventListener('storage', handleStorage)
      window.clearInterval(interval)
    }
  }, [isAuthenticated])
}

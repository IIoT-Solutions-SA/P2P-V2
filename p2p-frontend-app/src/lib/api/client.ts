import { buildApiUrl } from "@/config/environment"
import type { ApiMessageResponse } from "@/lib/api/types"

export class ApiError extends Error {
  readonly statusCode: number
  readonly payload: unknown

  constructor(message: string, statusCode: number, payload: unknown) {
    super(message)
    this.name = "ApiError"
    this.statusCode = statusCode
    this.payload = payload
  }
}

type ApiFetchOptions = Omit<RequestInit, "body"> & {
  body?: BodyInit | object | null
}

const isPlainObjectBody = (body: ApiFetchOptions["body"]): body is object => {
  return Boolean(body) && !(body instanceof FormData) && !(body instanceof Blob) && !(body instanceof URLSearchParams)
}

const getMessageFromPayload = (payload: unknown, fallback: string) => {
  if (payload && typeof payload === "object") {
    const candidate = payload as ApiMessageResponse
    return candidate.message || candidate.detail || fallback
  }

  return fallback
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const headers = new Headers(options.headers)
  const body = options.body

  if (isPlainObjectBody(body)) {
    headers.set("Content-Type", headers.get("Content-Type") || "application/json")
  }

  const response = await fetch(buildApiUrl(path), {
    ...options,
    headers,
    credentials: options.credentials ?? "include",
    body: isPlainObjectBody(body) ? JSON.stringify(body) : body ?? undefined,
  })

  const contentType = response.headers.get("content-type") || ""
  const payload = contentType.includes("application/json") ? await response.json() : await response.text()

  if (!response.ok) {
    throw new ApiError(getMessageFromPayload(payload, response.statusText), response.status, payload)
  }

  return payload as T
}

export const api = {
  get: <T>(path: string, options?: ApiFetchOptions) => apiFetch<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: ApiFetchOptions["body"], options?: ApiFetchOptions) =>
    apiFetch<T>(path, { ...options, method: "POST", body }),
  put: <T>(path: string, body?: ApiFetchOptions["body"], options?: ApiFetchOptions) =>
    apiFetch<T>(path, { ...options, method: "PUT", body }),
  delete: <T>(path: string, options?: ApiFetchOptions) => apiFetch<T>(path, { ...options, method: "DELETE" }),
}


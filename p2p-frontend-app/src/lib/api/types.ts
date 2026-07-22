import type { Organization, User } from "@/types/auth"

export type ApiStatus = "OK" | "ERROR" | string

export interface ApiMessageResponse {
  status?: ApiStatus
  message?: string
  detail?: string
}

export interface CurrentUserResponse {
  user: User
  organization: Organization
}

export interface MfaRequiredResponse {
  status: "MFA_REQUIRED"
  challengeId: string
  email?: string
  message?: string
}

export interface AuthOkResponse extends ApiMessageResponse {
  status: "OK"
}

export interface SignupResponse extends AuthOkResponse {
  requiresOTPVerification?: boolean
  requiresEmailVerification?: boolean
  email?: string
}

export interface OtpErrorResponse extends ApiMessageResponse {
  challengeId?: string
  attemptsRemaining?: number
  retryAfterSeconds?: number
  requiresManualLogin?: boolean
}

export type SigninResponse = AuthOkResponse | MfaRequiredResponse | ApiMessageResponse

export interface InvitationValidationResponse {
  valid: boolean
  email?: string
  invited_by_name?: string
  expires_at?: string
  error?: string
  organization_name?: string
  industry?: string
  organization_size?: string
  city?: string
  country?: string
}

export interface ResetPasswordResponse extends ApiMessageResponse {
  formFields?: Array<{ id: string; error: string }>
  userId?: string
}

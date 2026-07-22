import type { LoginCredentials, SignupData } from "@/types/auth"
import { api } from "@/lib/api/client"
import type {
  ApiMessageResponse,
  CurrentUserResponse,
  InvitationValidationResponse,
  OtpErrorResponse,
  ResetPasswordResponse,
  SigninResponse,
  SignupResponse,
} from "@/lib/api/types"

export const authApi = {
  me: () => api.get<CurrentUserResponse>("/api/v1/auth/me"),

  signin: (credentials: LoginCredentials) =>
    api.post<SigninResponse>("/api/v1/auth/custom-signin", credentials),

  signup: (data: SignupData) => {
    const payload = {
      firstName: data.firstName,
      lastName: data.lastName,
      email: data.email,
      password: data.password,
      title: data.title,
      companyName: data.organizationName,
      industrySector: data.industry,
      companySize: data.organizationSize,
      city: data.city,
      ...(data.inviteToken && { inviteToken: data.inviteToken }),
      ...(data.isInvited && { isInvited: data.isInvited }),
      ...(data.role && { role: data.role }),
    }

    return api.post<SignupResponse>("/api/v1/auth/custom-signup", payload)
  },

  verifyLoginOtp: (email: string, challengeId: string, code: string) =>
    api.post<OtpErrorResponse>("/api/v1/auth/verify-login-otp", { email, challengeId, code }),

  verifySignupOtp: (email: string, code: string, inviteToken?: string) =>
    api.post<OtpErrorResponse>("/api/v1/auth/verify-signup-otp", { email, code, ...(inviteToken && { inviteToken }) }),

  resendOtp: (email: string, purpose: "signup_verify" | "login_mfa") =>
    api.post<OtpErrorResponse>("/api/v1/auth/resend-otp", { email, purpose }, { credentials: "include" }),

  forgotPassword: (email: string) =>
    api.post<ApiMessageResponse>("/api/v1/auth/forgot-password", { email }),

  resetPassword: (token: string, newPassword: string) =>
    api.post<ResetPasswordResponse>("/api/v1/auth/reset-password", { token, newPassword }),

  verifyEmailToken: (token: string) =>
    api.post<ApiMessageResponse>("/api/v1/auth/user/email/verify", { method: "token", token }),

  validateInvitation: (token: string) =>
    api.get<InvitationValidationResponse>(`/api/v1/invites/validate/${encodeURIComponent(token)}`),

  signout: () => api.post<ApiMessageResponse>("/api/v1/auth/custom-signout"),
}

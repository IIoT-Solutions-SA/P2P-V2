import { type FormEvent, type ReactNode, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { AlertCircle, ArrowRight, Building2, Eye, EyeOff, Loader2, LockKeyhole, Mail, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/contexts/AuthContext"
import { buildApiUrl } from "@/config/environment"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold, FieldError } from "@/components/auth/AuthScaffold"

const blockedDomains = new Set(["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com", "icloud.com", "live.com", "msn.com"])
const defaultAuthContext = [
  { icon: Mail, title: "Use your work email", body: "PeerLink uses company domains to keep workspaces tied to verified organizations.", tone: "blue" as const },
  { icon: ShieldCheck, title: "Verify new devices", body: "A six-digit code may be required before a new browser receives a session.", tone: "teal" as const },
  { icon: Building2, title: "Organization access follows sign-in", body: "Workspace membership and roles are resolved by the existing backend contracts.", tone: "amber" as const },
]

const getEmailIssue = (value: string) => {
  const trimmed = value.trim()
  if (!trimmed) return ""
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) return "Enter a valid work email address."
  const domain = trimmed.split("@")[1]?.toLowerCase()
  if (blockedDomains.has(domain)) return "Personal email addresses are not allowed. Use your company email."
  return ""
}

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || "/dashboard"
  const successMessage = location.state?.message || ""
  const { login, refreshProfile } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [trustDevice, setTrustDevice] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<ReactNode>("")
  const [emailError, setEmailError] = useState("")

  const handleEmailChange = (value: string) => {
    setEmail(value)
    setEmailError(getEmailIssue(value))
  }

  const uploadPendingPicture = async () => {
    const pendingPicture = localStorage.getItem("pendingProfilePicture")
    const pendingPictureType = localStorage.getItem("pendingProfilePictureType")
    if (!pendingPicture || !pendingPictureType) return

    try {
      const response = await fetch(pendingPicture)
      const blob = await response.blob()
      const file = new File([blob], "profile-picture", { type: pendingPictureType })
      const formData = new FormData()
      formData.append("file", file)
      await fetch(buildApiUrl("/api/v1/media/profile-picture"), {
        method: "POST",
        body: formData,
        credentials: "include",
      })
      await refreshProfile()
      localStorage.removeItem("pendingProfilePicture")
      localStorage.removeItem("pendingProfilePictureType")
    } catch (uploadError) {
      console.warn("Profile picture upload failed:", uploadError)
    }
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const issue = getEmailIssue(email)
    setEmailError(issue)
    if (issue) return

    setError("")
    setIsLoading(true)

    try {
      const result = await login({ email: email.trim().toLowerCase(), password })

      if (result?.mfaRequired) {
        navigate(`/verify-otp?purpose=login_mfa&email=${encodeURIComponent(result.email)}`, {
          state: { challengeId: result.challengeId, trustDevice },
        })
        return
      }

      await uploadPendingPicture()
      navigate(from, { replace: true })
    } catch (caught) {
      const message = caught instanceof Error ? caught.message : "Login failed"
      if (message.includes("verify your email") || message.includes("EMAIL_NOT_VERIFIED")) {
        setError(
          <span>
            Please verify your email before signing in.{" "}
            <button
              type="button"
              onClick={() => navigate(`/verify-otp?purpose=signup_verify&email=${encodeURIComponent(email)}`)}
              className="font-bold underline"
            >
              Enter verification code
            </button>
          </span>,
        )
      } else {
        setError(message)
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthScaffold
      eyebrow="Secure manufacturer access"
      title="Enter a trusted manufacturing network."
      copy="Access is limited to verified manufacturers, partners, and invited team members."
      contextTitle="Before you enter"
      contextItems={defaultAuthContext}
    >
      <AuthCard>
        <AuthHeading title="Welcome back" subtitle="Sign in with your work identity to access PeerLink." />
        {successMessage ? <AuthAlert tone="success">{successMessage}</AuthAlert> : null}
        {error ? <AuthAlert tone="error"><span className="inline-flex items-start gap-2"><AlertCircle className="mt-0.5 size-4 shrink-0" />{error}</span></AuthAlert> : null}

        <form onSubmit={handleSubmit} className="grid gap-4">
          <div>
            <div className="mb-2 flex items-center justify-between gap-3">
              <label htmlFor="email" className="text-xs font-bold text-[#07161d]">Email address</label>
              <span className="text-[10px] text-[var(--peer-muted)]">Company domain required</span>
            </div>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
              <Input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => handleEmailChange(event.target.value)}
                className={`h-12 rounded-[5px] bg-white/70 pl-11 ${emailError ? "border-[var(--peer-danger)]" : ""}`}
                required
              />
            </div>
            <FieldError message={emailError} />
          </div>

          <div>
            <label htmlFor="password" className="mb-2 block text-xs font-bold text-[#07161d]">Password</label>
            <div className="relative">
              <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="h-12 rounded-[5px] bg-white/70 pl-11 pr-11"
                required
              />
              <button
                type="button"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((value) => !value)}
                className="absolute right-2 top-1/2 grid size-9 -translate-y-1/2 place-items-center text-[var(--peer-muted)]"
              >
                {showPassword ? <EyeOff className="size-5" /> : <Eye className="size-5" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between gap-3 text-xs">
            <label className="flex items-center gap-2 text-[var(--peer-muted)]">
              <input
                type="checkbox"
                checked={trustDevice}
                onChange={(event) => setTrustDevice(event.target.checked)}
                className="size-4 accent-[var(--peer-blue)]"
              />
              Trust this device
            </label>
            <Link className="font-bold text-[var(--peer-blue)]" to="/forgot-password">Forgot password?</Link>
          </div>

          <Button type="submit" disabled={isLoading} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
            {isLoading ? <><Loader2 className="size-4 animate-spin" />Verifying access...</> : <>Sign in<ArrowRight className="size-4" /></>}
          </Button>
        </form>

        <div className="my-6 grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-xs text-[var(--peer-muted)] before:border-t before:border-[var(--peer-line)] after:border-t after:border-[var(--peer-line)]">or</div>
        <p className="text-center text-sm text-[var(--peer-muted)]">
          New to PeerLink? <Link className="font-bold text-[var(--peer-blue)]" to="/signup">Create organization account</Link>
        </p>
        <p className="mt-5 flex items-center justify-center gap-2 text-center text-xs text-[var(--peer-muted)]">
          <LockKeyhole className="size-4" /> New devices may require a verification code.
        </p>
      </AuthCard>
    </AuthScaffold>
  )
}

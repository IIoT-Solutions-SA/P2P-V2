import { type FormEvent, useCallback, useEffect, useRef, useState } from "react"
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom"
import { AlertCircle, CheckCircle2, Loader2, Mail, RefreshCw, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { authApi } from "@/lib/api/auth"
import { ApiError } from "@/lib/api/client"
import type { OtpErrorResponse } from "@/lib/api/types"
import { useAuth } from "@/contexts/AuthContext"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold } from "@/components/auth/AuthScaffold"

const OTP_EXPIRY_SECS = 7 * 60

export default function OtpVerification() {
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { verifyLoginOtp, fetchProfile } = useAuth()
  const purpose = searchParams.get("purpose") || "login_mfa"
  const email = searchParams.get("email") || ""
  const inviteToken = searchParams.get("inviteToken") || (location.state as { inviteToken?: string } | null)?.inviteToken || ""
  const [challengeId, setChallengeId] = useState((location.state as { challengeId?: string } | null)?.challengeId || "")
  const [digits, setDigits] = useState(["", "", "", "", "", ""])
  const inputRefs = useRef<Array<HTMLInputElement | null>>([null, null, null, null, null, null])
  const [isVerifying, setIsVerifying] = useState(false)
  const [error, setError] = useState("")
  const [attemptsRemaining, setAttemptsRemaining] = useState<number | null>(null)
  const [success, setSuccess] = useState(false)
  const [timeLeft, setTimeLeft] = useState(OTP_EXPIRY_SECS)
  const [resendCooldown, setResendCooldown] = useState(0)
  const [isResending, setIsResending] = useState(false)

  const isLoginMfa = purpose === "login_mfa"
  const code = digits.join("")
  const isComplete = code.length === 6
  const maskedEmail = email.replace(/(.{2}).*@/, "$1***@")

  useEffect(() => {
    if (timeLeft <= 0 || success) return
    const timer = window.setTimeout(() => setTimeLeft((value) => value - 1), 1000)
    return () => window.clearTimeout(timer)
  }, [timeLeft, success])

  useEffect(() => {
    if (resendCooldown <= 0) return
    const timer = window.setTimeout(() => setResendCooldown((value) => value - 1), 1000)
    return () => window.clearTimeout(timer)
  }, [resendCooldown])

  const focusInput = (index: number) => inputRefs.current[index]?.focus()

  const resetDigits = useCallback(() => {
    setDigits(["", "", "", "", "", ""])
    window.setTimeout(() => focusInput(0), 0)
  }, [])

  const handleDigitChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1)
    const next = [...digits]
    next[index] = digit
    setDigits(next)
    setError("")
    if (digit && index < 5) focusInput(index + 1)
  }

  const handleKeyDown = (index: number, event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Backspace") {
      if (digits[index]) {
        const next = [...digits]
        next[index] = ""
        setDigits(next)
      } else if (index > 0) {
        focusInput(index - 1)
      }
    }
    if (event.key === "ArrowLeft" && index > 0) focusInput(index - 1)
    if (event.key === "ArrowRight" && index < 5) focusInput(index + 1)
  }

  const handlePaste = (event: React.ClipboardEvent) => {
    event.preventDefault()
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6)
    if (!pasted) return
    const next = ["", "", "", "", "", ""]
    pasted.split("").forEach((digit, index) => {
      next[index] = digit
    })
    setDigits(next)
    focusInput(Math.min(pasted.length, 5))
  }

  const readOtpError = (caught: unknown) => {
    if (caught instanceof ApiError && caught.payload && typeof caught.payload === "object") return caught.payload as OtpErrorResponse
    if (caught instanceof Error) return { status: "ERROR", message: caught.message } satisfies OtpErrorResponse
    return { status: "ERROR", message: "Verification failed. Please try again." } satisfies OtpErrorResponse
  }

  const handleSubmit = async (event?: FormEvent) => {
    event?.preventDefault()
    if (!isComplete || isVerifying) return
    setError("")
    setIsVerifying(true)

    try {
      if (isLoginMfa) {
        await verifyLoginOtp(email, challengeId, code)
        setSuccess(true)
        window.setTimeout(() => navigate("/dashboard", { replace: true }), 700)
      } else {
        const result = await authApi.verifySignupOtp(email, code, inviteToken)
        if (result.status === "OK") {
          if (result.requiresManualLogin) {
            navigate("/login", { replace: true, state: { message: "Email verified. Please sign in to continue." } })
          } else {
            await fetchProfile()
            setSuccess(true)
            window.setTimeout(() => navigate("/dashboard", { replace: true }), 700)
          }
        } else {
          setError(result.message || "Verification failed. Please try again.")
        }
      }
    } catch (caught) {
      const result = readOtpError(caught)
      setError(result.message || "Verification failed. Please try again.")
      setAttemptsRemaining(result.attemptsRemaining ?? null)
      if (result.status === "INVALID_CODE") resetDigits()
      if (result.status === "OTP_EXPIRED") setTimeLeft(0)
      if (result.status === "MAX_ATTEMPTS_REACHED") setAttemptsRemaining(0)
    } finally {
      setIsVerifying(false)
    }
  }

  const handleResend = async () => {
    if (resendCooldown > 0 || isResending) return
    setIsResending(true)
    setError("")

    try {
      const result = await authApi.resendOtp(email, purpose as "signup_verify" | "login_mfa")
      setTimeLeft(OTP_EXPIRY_SECS)
      setAttemptsRemaining(null)
      setResendCooldown(result.retryAfterSeconds || 60)
      if (result.challengeId) setChallengeId(result.challengeId)
      resetDigits()
    } catch (caught) {
      const result = readOtpError(caught)
      if (result.status === "RATE_LIMITED") setResendCooldown(result.retryAfterSeconds || 60)
      setError(result.message || "Failed to resend code. Please try again.")
    } finally {
      setIsResending(false)
    }
  }

  const formatTime = (seconds: number) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`

  return (
    <AuthScaffold
      eyebrow={isLoginMfa ? "Device verification" : "Email verification"}
      steps={[
        { label: isLoginMfa ? "Credentials" : "Account", detail: isLoginMfa ? "Password accepted" : "Profile created" },
        { label: "Code", detail: "Enter six digits" },
        { label: "Session", detail: "Continue securely" },
      ]}
      activeStep={success ? 3 : 2}
      contextTitle={isLoginMfa ? "New device check" : "Account activation"}
      contextItems={[
        { icon: isLoginMfa ? ShieldCheck : Mail, title: isLoginMfa ? "MFA required" : "Email code sent", body: `A six-digit code was sent to ${maskedEmail || "your work email"}.`, tone: "blue" },
        { icon: RefreshCw, title: "Resend with cooldown", body: "The resend action follows the backend rate limit and challenge contract.", tone: "teal" },
        { icon: CheckCircle2, title: "Session behavior preserved", body: isLoginMfa ? "A successful code creates the SuperTokens session." : "Signup verification can auto-create the session when backend allows it.", tone: "success" },
      ]}
    >
      <AuthCard>
        {success ? (
          <div className="text-center">
            <CheckCircle2 className="mx-auto mb-5 size-16 text-[var(--peer-success)]" />
            <AuthHeading title={isLoginMfa ? "You are in" : "Email verified"} subtitle="Redirecting to your workspace..." />
          </div>
        ) : (
          <>
            <AuthHeading title={isLoginMfa ? "Verify your identity" : "Verify your email"} subtitle={<span>Enter the six-digit code sent to <strong className="text-[var(--peer-blue)]">{maskedEmail || "your work email"}</strong>.</span>} />
            {error ? <AuthAlert tone="error"><span className="inline-flex items-start gap-2"><AlertCircle className="mt-0.5 size-4 shrink-0" />{error}</span>{attemptsRemaining !== null && attemptsRemaining > 0 ? <span className="mt-1 block">{attemptsRemaining} attempts remaining.</span> : null}</AuthAlert> : null}
            {timeLeft === 0 ? <AuthAlert tone="warning">Code expired. Request a new code below.</AuthAlert> : null}

            <form onSubmit={handleSubmit} className="grid gap-5">
              <div className="grid grid-cols-6 gap-2 sm:gap-3" onPaste={handlePaste}>
                {digits.map((digit, index) => (
                  <input
                    key={index}
                    ref={(element) => { inputRefs.current[index] = element }}
                    type="text"
                    inputMode="numeric"
                    aria-label={`Digit ${index + 1}`}
                    maxLength={1}
                    value={digit}
                    onChange={(event) => handleDigitChange(index, event.target.value)}
                    onKeyDown={(event) => handleKeyDown(index, event)}
                    disabled={isVerifying || attemptsRemaining === 0 || timeLeft === 0}
                    className={`aspect-square min-h-11 rounded-[5px] border bg-white text-center font-display text-xl font-bold text-[var(--peer-ink)] outline-none focus:border-[var(--peer-blue)] focus:ring-4 focus:ring-[rgba(23,105,223,.11)] sm:min-h-14 ${error ? "border-[var(--peer-danger)]" : digit ? "border-[var(--peer-blue)]" : "border-[var(--peer-line)]"}`}
                  />
                ))}
              </div>

              {timeLeft > 0 ? <p className="text-center text-sm text-[var(--peer-muted)]">Code expires in <strong>{formatTime(timeLeft)}</strong></p> : null}

              <Button type="submit" disabled={!isComplete || isVerifying || attemptsRemaining === 0 || timeLeft === 0} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc] disabled:bg-slate-400">
                {isVerifying ? <><Loader2 className="size-4 animate-spin" />Verifying...</> : isLoginMfa ? "Confirm and sign in" : "Verify email"}
              </Button>
            </form>

            <div className="mt-5 text-center">
              <p className="mb-2 text-sm text-[var(--peer-muted)]">Did not receive a code?</p>
              <button type="button" onClick={handleResend} disabled={resendCooldown > 0 || isResending} className="inline-flex items-center gap-2 text-sm font-bold text-[var(--peer-blue)] disabled:text-[var(--peer-muted)]">
                {isResending ? <><Loader2 className="size-4 animate-spin" />Sending...</> : resendCooldown > 0 ? <><RefreshCw className="size-4" />Resend in {resendCooldown}s</> : <><RefreshCw className="size-4" />Resend code</>}
              </button>
            </div>

            <p className="mt-6 text-center text-sm text-[var(--peer-muted)]">
              Wrong account? <Link className="font-bold text-[var(--peer-blue)]" to="/login">Sign in again</Link>
            </p>
          </>
        )}
      </AuthCard>
    </AuthScaffold>
  )
}

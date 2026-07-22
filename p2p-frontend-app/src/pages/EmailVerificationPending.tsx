import { useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { CheckCircle2, Loader2, Mail, RefreshCw, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { authApi } from "@/lib/api/auth"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold } from "@/components/auth/AuthScaffold"

export default function EmailVerificationPending() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const email = searchParams.get("email") || ""
  const [resending, setResending] = useState(false)
  const [cooldown, setCooldown] = useState(0)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  const handleResendCode = async () => {
    if (!email || cooldown > 0) return
    setResending(true)
    setMessage(null)

    try {
      const result = await authApi.resendOtp(email, "signup_verify")
      const retryAfter = result.retryAfterSeconds || 60
      setCooldown(retryAfter)
      setMessage({ type: "success", text: "A new verification code has been sent to your work email." })
      const interval = window.setInterval(() => {
        setCooldown((value) => {
          if (value <= 1) {
            window.clearInterval(interval)
            return 0
          }
          return value - 1
        })
      }, 1000)
    } catch (caught) {
      setMessage({ type: "error", text: caught instanceof Error ? caught.message : "Failed to resend verification code." })
    } finally {
      setResending(false)
    }
  }

  return (
    <AuthScaffold
      eyebrow="Email verification"
      steps={[{ label: "Account", detail: "Profile created" }, { label: "Verify", detail: "Enter email code" }, { label: "Workspace", detail: "Continue securely" }]}
      activeStep={2}
      contextTitle="Verification state"
      contextItems={[
        { icon: Mail, title: "Check your work email", body: "The active backend flow sends a six-digit signup verification code.", tone: "blue" },
        { icon: RefreshCw, title: "Resend safely", body: "Resend uses the same OTP cooldown as the verification page.", tone: "teal" },
        { icon: ShieldCheck, title: "No session yet", body: "Access starts only after the signup verification contract succeeds.", tone: "amber" },
      ]}
    >
      <AuthCard className="text-center">
        <Mail className="mx-auto mb-5 size-16 text-[var(--peer-blue)]" />
        <AuthHeading title="Check your email" subtitle={<span>We sent a verification code to <strong className="text-[var(--peer-blue)]">{email || "your work email"}</strong>.</span>} />
        {message ? <AuthAlert tone={message.type === "success" ? "success" : "error"}>{message.text}</AuthAlert> : null}
        <div className="grid gap-3">
          <Button onClick={() => navigate(`/verify-otp?purpose=signup_verify&email=${encodeURIComponent(email)}`)} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
            Enter verification code
          </Button>
          <Button onClick={handleResendCode} disabled={!email || resending || cooldown > 0} variant="outline" className="h-12 rounded-[5px]">
            {resending ? <><Loader2 className="size-4 animate-spin" />Sending...</> : cooldown > 0 ? `Resend in ${cooldown}s` : "Resend code"}
          </Button>
          <Button onClick={() => navigate("/login")} variant="ghost" className="h-12 rounded-[5px]">Back to sign in</Button>
        </div>
        <div className="mt-6 border-t border-[var(--peer-line)] pt-5 text-xs text-[var(--peer-muted)]">
          <CheckCircle2 className="mx-auto mb-2 size-4 text-[var(--peer-success)]" />
          Check spam or ask your organization administrator if the email does not arrive.
        </div>
      </AuthCard>
    </AuthScaffold>
  )
}

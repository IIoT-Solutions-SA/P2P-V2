import { useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { ArrowRight, CheckCircle2, Loader2, Mail, ShieldCheck, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { authApi } from "@/lib/api/auth"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold } from "@/components/auth/AuthScaffold"

export default function EmailVerificationSuccess() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<"ready" | "verifying" | "success" | "error">("ready")
  const [message, setMessage] = useState("Click the button below to verify your email address.")

  const handleVerifyClick = async () => {
    const token = searchParams.get("token")
    if (!token) {
      setStatus("error")
      setMessage("No verification token found.")
      return
    }

    setStatus("verifying")
    setMessage("Verifying your email...")

    try {
      const result = await authApi.verifyEmailToken(token)
      if (result.status === "OK") {
        setStatus("success")
        setMessage("Email verified successfully. You can now sign in.")
        window.setTimeout(() => navigate("/login", { state: { message: "Email verified successfully. Please sign in." } }), 1800)
      } else {
        setStatus("error")
        setMessage(result.message || "Verification failed. The link may be expired or already used.")
      }
    } catch (caught) {
      setStatus("error")
      setMessage(caught instanceof Error ? caught.message : "Verification failed. The link may be expired or invalid.")
    }
  }

  const symbol = {
    ready: <Mail className="size-12 text-[var(--peer-blue)]" />,
    verifying: <Loader2 className="size-12 animate-spin text-[var(--peer-blue)]" />,
    success: <CheckCircle2 className="size-12 text-[var(--peer-success)]" />,
    error: <XCircle className="size-12 text-[var(--peer-danger)]" />,
  }[status]

  return (
    <AuthScaffold
      eyebrow="Email verification"
      steps={[{ label: "Link", detail: "Open secure email link" }, { label: "Verify", detail: "Backend validates token" }, { label: "Sign in", detail: "Return to login" }]}
      activeStep={status === "success" ? 3 : 2}
      contextTitle="Secure link state"
      contextItems={[
        { icon: Mail, title: "Token verification", body: "This route preserves the existing email-verification link behavior.", tone: "blue" },
        { icon: ShieldCheck, title: "No account changes on failure", body: "Invalid or expired links stop without creating a new session.", tone: "teal" },
        { icon: CheckCircle2, title: "Continue to sign in", body: "Successful verification returns users to the normal login flow.", tone: "success" },
      ]}
    >
      <AuthCard className="text-center">
        <div className="mx-auto mb-5 grid size-20 place-items-center rounded-full bg-white">
          {symbol}
        </div>
        <AuthHeading
          title={status === "ready" ? "Verify your email" : status === "verifying" ? "Verifying email" : status === "success" ? "Email verified" : "Verification failed"}
          subtitle={message}
        />

        {status === "ready" ? (
          <Button onClick={handleVerifyClick} className="h-12 w-full rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
            Verify email address
          </Button>
        ) : null}
        {status === "verifying" ? <AuthAlert tone="info">Checking this secure link with the authentication service...</AuthAlert> : null}
        {status === "success" ? (
          <AuthAlert tone="success">Your account is active. Redirecting to sign in...</AuthAlert>
        ) : null}
        {status === "error" ? (
          <div className="grid gap-3">
            <AuthAlert tone="error">{message}</AuthAlert>
            <Button onClick={() => navigate("/forgot-password")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
              Recover account<ArrowRight className="size-4" />
            </Button>
            <Button onClick={() => navigate("/login")} variant="outline" className="h-12 rounded-[5px]">Back to sign in</Button>
          </div>
        ) : null}
      </AuthCard>
    </AuthScaffold>
  )
}

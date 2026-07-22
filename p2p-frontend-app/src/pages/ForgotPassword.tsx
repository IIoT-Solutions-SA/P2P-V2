import { type FormEvent, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, CheckCircle2, Loader2, Mail, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/lib/api/auth"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold } from "@/components/auth/AuthScaffold"

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      const result = await authApi.forgotPassword(email.trim().toLowerCase())
      if (result.status === "OK") setSuccess(true)
      else setError(result.message || "Failed to send reset email")
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "An unexpected error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthScaffold
      eyebrow="Password recovery"
      title="Recover access without exposing account status."
      copy="PeerLink uses a privacy-safe reset flow that does not reveal whether an email exists."
      contextTitle="Recovery safeguards"
      contextItems={[
        { icon: Mail, title: "Privacy-safe response", body: "The backend returns the same confirmation whether or not an account exists.", tone: "blue" },
        { icon: ShieldCheck, title: "Time-limited link", body: "SuperTokens reset links expire and can only be used through the existing backend flow.", tone: "teal" },
        { icon: CheckCircle2, title: "Return to sign in", body: "After reset, sign in again with your new password and device verification if required.", tone: "success" },
      ]}
    >
      <AuthCard>
        <button type="button" onClick={() => navigate("/login")} className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-[var(--peer-muted)] hover:text-[var(--peer-ink)]">
          <ArrowLeft className="size-4" />Back to sign in
        </button>

        {success ? (
          <div className="text-center">
            <CheckCircle2 className="mx-auto mb-5 size-16 text-[var(--peer-success)]" />
            <AuthHeading title="Request received" subtitle="If an account exists with this work email, a password reset link will arrive shortly." />
            <AuthAlert tone="info" title="What happens next">
              Check your inbox, use the reset link, then create a new password. The link expires according to the existing authentication service policy.
            </AuthAlert>
            <div className="grid gap-3">
              <Button onClick={() => navigate("/login")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">Return to sign in</Button>
              <Button variant="outline" onClick={() => { setSuccess(false); setEmail("") }} className="h-12 rounded-[5px]">Try another email</Button>
            </div>
          </div>
        ) : (
          <>
            <AuthHeading title="Forgot password?" subtitle="Enter your work email and we will send reset instructions if an account exists." />
            {error ? <AuthAlert tone="error">{error}</AuthAlert> : null}
            <form onSubmit={handleSubmit} className="grid gap-4">
              <div>
                <label htmlFor="reset-email" className="mb-2 block text-xs font-bold text-[#07161d]">Work email</label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
                  <Input id="reset-email" type="email" autoComplete="email" placeholder="you@company.com" value={email} onChange={(event) => setEmail(event.target.value)} className="h-12 rounded-[5px] bg-white/70 pl-11" required />
                </div>
              </div>
              <Button type="submit" disabled={isLoading} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
                {isLoading ? <><Loader2 className="size-4 animate-spin" />Sending reset link...</> : "Send reset link"}
              </Button>
            </form>
            <p className="mt-6 text-center text-sm text-[var(--peer-muted)]">
              Remember your password? <Link className="font-bold text-[var(--peer-blue)]" to="/login">Sign in</Link>
            </p>
          </>
        )}
      </AuthCard>
    </AuthScaffold>
  )
}

import { type FormEvent, useEffect, useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { ArrowRight, CheckCircle2, Eye, EyeOff, Loader2, LockKeyhole, ShieldCheck, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/lib/api/auth"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold, PasswordRequirements } from "@/components/auth/AuthScaffold"

export default function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get("token") || ""
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    if (!token) setError("Invalid or missing reset token. Please request a new password reset link.")
  }, [token])

  const validatePassword = () => {
    if (newPassword.length < 8 || !/[a-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) return "Password must be at least 8 characters with a lowercase letter and a number."
    if (newPassword !== confirmPassword) return "Passwords do not match."
    return ""
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const issue = validatePassword()
    if (issue) {
      setError(issue)
      return
    }

    setError("")
    setIsLoading(true)

    try {
      const result = await authApi.resetPassword(token, newPassword)
      if (result.status === "OK") {
        setSuccess(true)
        window.setTimeout(() => {
          navigate("/login", { state: { message: "Password reset successful. Please sign in with your new password." } })
        }, 2500)
      } else if (result.status === "FIELD_ERROR" && result.formFields) {
        const passwordError = result.formFields.find((field) => field.id === "password")
        setError(passwordError?.error || result.message || "Password does not meet requirements.")
      } else {
        setError(result.message || "Failed to reset password.")
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "An unexpected error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthScaffold
      eyebrow="Password recovery"
      title="Create a new password from a secure link."
      copy="Reset tokens are handled by the existing SuperTokens-backed endpoint."
      contextTitle="Password reset"
      contextItems={[
        { icon: ShieldCheck, title: "Verified reset link", body: "The backend validates the token before changing credentials.", tone: "teal" },
        { icon: LockKeyhole, title: "Password policy", body: "Frontend guidance mirrors the backend password reset contract.", tone: "blue" },
        { icon: CheckCircle2, title: "Sign in again", body: "After reset, you return to the normal login and MFA flow.", tone: "success" },
      ]}
    >
      <AuthCard>
        {success ? (
          <div className="text-center">
            <CheckCircle2 className="mx-auto mb-5 size-16 text-[var(--peer-success)]" />
            <AuthHeading title="Password reset complete" subtitle="Redirecting you to sign in with the new password." />
            <Button onClick={() => navigate("/login")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
              Go to sign in<ArrowRight className="size-4" />
            </Button>
          </div>
        ) : (
          <>
            <AuthHeading title="Reset password" subtitle="Create a new password for your PeerLink account." />
            {error ? <AuthAlert tone={token ? "error" : "warning"}>{error}</AuthAlert> : null}
            {!token ? (
              <div className="text-center">
                <XCircle className="mx-auto mb-5 size-12 text-[var(--peer-danger)]" />
                <Button onClick={() => navigate("/forgot-password")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">Request a new link</Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="grid gap-4">
                <PasswordField label="New password" value={newPassword} onChange={setNewPassword} show={showNewPassword} onToggle={() => setShowNewPassword((value) => !value)} />
                <PasswordRequirements password={newPassword} />
                <PasswordField label="Confirm new password" value={confirmPassword} onChange={setConfirmPassword} show={showConfirmPassword} onToggle={() => setShowConfirmPassword((value) => !value)} />
                <Button type="submit" disabled={isLoading} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
                  {isLoading ? <><Loader2 className="size-4 animate-spin" />Resetting password...</> : "Reset password"}
                </Button>
              </form>
            )}
            <p className="mt-6 text-center text-sm text-[var(--peer-muted)]">
              Remember your password? <Link className="font-bold text-[var(--peer-blue)]" to="/login">Sign in</Link>
            </p>
          </>
        )}
      </AuthCard>
    </AuthScaffold>
  )
}

function PasswordField({ label, value, onChange, show, onToggle }: { label: string; value: string; onChange: (value: string) => void; show: boolean; onToggle: () => void }) {
  return (
    <div>
      <label className="mb-2 block text-xs font-bold text-[#07161d]">{label}</label>
      <div className="relative">
        <LockKeyhole className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
        <Input type={show ? "text" : "password"} value={value} onChange={(event) => onChange(event.target.value)} placeholder={label} className="h-12 rounded-[5px] bg-white/70 pl-11 pr-11" required />
        <button type="button" onClick={onToggle} aria-label={show ? "Hide password" : "Show password"} className="absolute right-2 top-1/2 grid size-9 -translate-y-1/2 place-items-center text-[var(--peer-muted)]">
          {show ? <EyeOff className="size-5" /> : <Eye className="size-5" />}
        </button>
      </div>
    </div>
  )
}

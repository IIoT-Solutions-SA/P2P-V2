import { type FormEvent, useEffect, useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { ArrowRight, BriefcaseBusiness, Building2, Eye, EyeOff, Loader2, LockKeyhole, Mail, ShieldCheck, TicketCheck, User, UserCheck, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/contexts/AuthContext"
import { authApi } from "@/lib/api/auth"
import type { InvitationValidationResponse } from "@/lib/api/types"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold, PasswordRequirements } from "@/components/auth/AuthScaffold"

export default function MemberSignup() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { signup } = useAuth()
  const inviteToken = searchParams.get("token") || ""
  const inviteEmail = searchParams.get("email") || ""
  const [invitation, setInvitation] = useState<InvitationValidationResponse | null>(null)
  const [validatingToken, setValidatingToken] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [acceptedTerms, setAcceptedTerms] = useState(true)
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: inviteEmail,
    password: "",
    title: "",
  })

  useEffect(() => {
    let mounted = true
    const validateInvitation = async () => {
      if (!inviteToken) {
        if (!mounted) return
        setInvitation({ valid: false, error: "No invitation token provided" })
        setError("No invitation token provided")
        setValidatingToken(false)
        return
      }

      try {
        const data = await authApi.validateInvitation(inviteToken)
        if (!mounted) return
        setInvitation(data)
        if (data.valid && data.email) {
          setFormData((previous) => ({ ...previous, email: data.email || previous.email }))
        } else {
          setError(data.error || "Invalid or expired invitation")
        }
      } catch {
        if (!mounted) return
        setInvitation({ valid: false, error: "Failed to validate invitation" })
        setError("Failed to validate invitation")
      } finally {
        if (mounted) setValidatingToken(false)
      }
    }

    validateInvitation()
    return () => {
      mounted = false
    }
  }, [inviteToken])

  const validateForm = () => {
    if (!formData.firstName.trim() || !formData.lastName.trim() || !formData.email.trim() || !formData.password.trim()) return "Complete all required fields."
    if (formData.password.length < 8 || !/[a-z]/.test(formData.password) || !/[0-9]/.test(formData.password)) return "Password must be at least 8 characters with a lowercase letter and a number."
    if (formData.password !== confirmPassword) return "Passwords do not match."
    if (!acceptedTerms) return "Accept the terms and privacy policy to continue."
    return ""
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const issue = validateForm()
    if (issue) {
      setError(issue)
      return
    }

    setError("")
    setIsLoading(true)

    try {
      const signupResponse = await signup({
        firstName: formData.firstName,
        lastName: formData.lastName,
        email: formData.email,
        password: formData.password,
        title: formData.title || "Team Member",
        organizationName: invitation?.organization_name || "Organization",
        industry: invitation?.industry || "Manufacturing",
        organizationSize: invitation?.organization_size || "medium",
        city: invitation?.city || "Riyadh",
        country: invitation?.country || "Saudi Arabia",
        inviteToken,
        role: "member",
        isInvited: true,
      })

      if (signupResponse && typeof signupResponse === "object" && signupResponse.requiresOTPVerification) {
        navigate(`/verify-otp?purpose=signup_verify&email=${encodeURIComponent(formData.email)}&inviteToken=${encodeURIComponent(inviteToken)}`)
      } else {
        navigate("/dashboard")
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Signup failed")
    } finally {
      setIsLoading(false)
    }
  }

  if (validatingToken) {
    return (
      <AuthScaffold
        eyebrow="Member sign-up"
        steps={[{ label: "Invitation", detail: "Confirm your invitation" }, { label: "Profile", detail: "Create member profile" }, { label: "Verify", detail: "Secure your account" }]}
        activeStep={1}
        contextTitle="Your invitation"
        contextItems={[
          { icon: TicketCheck, title: "Checking invitation", body: "PeerLink is validating this invitation token against the backend.", tone: "blue" },
          { icon: ShieldCheck, title: "Secure activation", body: "Invalid, expired, or used invitations stop before account creation.", tone: "teal" },
        ]}
      >
        <AuthCard className="text-center">
          <Loader2 className="mx-auto mb-4 size-10 animate-spin text-[var(--peer-blue)]" />
          <AuthHeading title="Validating invitation" subtitle="Checking whether this team invitation is still active." />
        </AuthCard>
      </AuthScaffold>
    )
  }

  if (invitation && !invitation.valid) {
    return (
      <AuthScaffold
        eyebrow="Member sign-up"
        steps={[{ label: "Invitation", detail: "Confirm your invitation" }, { label: "Profile", detail: "Create member profile" }, { label: "Verify", detail: "Secure your account" }]}
        activeStep={1}
        contextTitle="Safe stopping point"
        contextItems={[
          { icon: XCircle, title: "Invitation unavailable", body: "The backend rejected this invitation token.", tone: "danger" },
          { icon: Mail, title: "Ask for a new invite", body: "An organization administrator can issue a fresh team invitation.", tone: "blue" },
        ]}
      >
        <AuthCard className="text-center">
          <XCircle className="mx-auto mb-5 size-16 text-[var(--peer-danger)]" />
          <AuthHeading title="Invalid invitation" subtitle={invitation.error || error || "This invitation is invalid or expired."} />
          <Button onClick={() => navigate("/login")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">Go to sign in</Button>
        </AuthCard>
      </AuthScaffold>
    )
  }

  return (
    <AuthScaffold
      eyebrow="Member sign-up"
      steps={[{ label: "Invitation", detail: "Confirm your invitation" }, { label: "Profile", detail: "Create member profile" }, { label: "Verify", detail: "Secure your account" }]}
      activeStep={2}
      wide
      contextTitle="Your invitation"
      contextItems={[
        { icon: Building2, title: invitation?.organization_name || "Organization", body: "Your account will be connected to this verified organization.", tone: "teal" },
        { icon: UserCheck, title: "Member access", body: "Your administrator controls role and workspace permissions.", tone: "blue" },
        { icon: ShieldCheck, title: "Secure activation", body: "The backend sends a signup verification code before the account is activated.", tone: "amber" },
      ]}
    >
      <AuthCard>
        <AuthHeading title="Join your team" subtitle="Create a member account using your organization invitation." />
        {invitation?.valid ? (
          <AuthAlert tone="info" title="Invitation recognized">
            {invitation.invited_by_name || "An administrator"} invited you to join {invitation.organization_name || "their organization"}.
            {invitation.expires_at ? ` This invitation expires on ${new Date(invitation.expires_at).toLocaleDateString()}.` : ""}
          </AuthAlert>
        ) : null}
        {error ? <AuthAlert tone="error">{error}</AuthAlert> : null}

        <form onSubmit={handleSubmit} className="grid gap-4">
          <div>
            <div className="mb-2 flex items-center justify-between gap-3">
              <label className="text-xs font-bold text-[#07161d]">Work email</label>
              <span className="text-[10px] text-[var(--peer-muted)]">Set by invitation</span>
            </div>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
              <Input type="email" value={formData.email} disabled className="h-12 rounded-[5px] bg-[#efeee9] pl-11" />
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <TextField icon={User} label="First name" value={formData.firstName} onChange={(value) => setFormData((previous) => ({ ...previous, firstName: value }))} placeholder="Ahmed" />
            <TextField icon={User} label="Last name" value={formData.lastName} onChange={(value) => setFormData((previous) => ({ ...previous, lastName: value }))} placeholder="Al-Faisal" />
          </div>
          <TextField icon={BriefcaseBusiness} label="Job title" value={formData.title} onChange={(value) => setFormData((previous) => ({ ...previous, title: value }))} placeholder="Operations Manager" />

          <PasswordField label="Create password" value={formData.password} onChange={(value) => setFormData((previous) => ({ ...previous, password: value }))} show={showPassword} onToggle={() => setShowPassword((value) => !value)} />
          <PasswordRequirements password={formData.password} />
          <PasswordField label="Confirm password" value={confirmPassword} onChange={setConfirmPassword} show={showConfirmPassword} onToggle={() => setShowConfirmPassword((value) => !value)} />

          <label className="flex items-start gap-2 text-xs text-[var(--peer-muted)]">
            <input type="checkbox" checked={acceptedTerms} onChange={(event) => setAcceptedTerms(event.target.checked)} className="mt-0.5 size-4 accent-[var(--peer-blue)]" />
            <span>I agree to the terms and privacy policy.</span>
          </label>

          <Button type="submit" disabled={isLoading} className="h-12 rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
            {isLoading ? <><Loader2 className="size-4 animate-spin" />Creating member account...</> : <>Create member account<ArrowRight className="size-4" /></>}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--peer-muted)]">
          Already registered? <Link className="font-bold text-[var(--peer-blue)]" to="/login">Sign in</Link>
        </p>
      </AuthCard>
    </AuthScaffold>
  )
}

function TextField({ icon: Icon, label, value, onChange, placeholder }: { icon: typeof User; label: string; value: string; onChange: (value: string) => void; placeholder: string }) {
  return (
    <div>
      <label className="mb-2 block text-xs font-bold text-[#07161d]">{label}</label>
      <div className="relative">
        <Icon className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
        <Input value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="h-12 rounded-[5px] bg-white/70 pl-11" required={label !== "Job title"} />
      </div>
    </div>
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

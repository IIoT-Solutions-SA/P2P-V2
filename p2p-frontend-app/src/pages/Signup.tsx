import { type FormEvent, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, ArrowRight, BriefcaseBusiness, Building2, Eye, EyeOff, Loader2, LockKeyhole, Mail, MapPin, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/contexts/AuthContext"
import type { SignupData } from "@/types/auth"
import { AuthAlert, AuthCard, AuthHeading, AuthScaffold, FieldError, PasswordRequirements } from "@/components/auth/AuthScaffold"
import { ProfilePictureEditor } from "@/components/ui/ProfilePictureEditor"

const industries = [
  "Electronics Manufacturing",
  "Automotive Manufacturing",
  "Plastics Manufacturing",
  "Textile Manufacturing",
  "Food & Beverage",
  "Pharmaceutical",
  "Chemical Processing",
  "Metal Processing",
  "Aerospace",
  "Other",
]

const organizationSizes = [
  { value: "startup", label: "Startup (1-10 employees)" },
  { value: "small", label: "Small (11-50 employees)" },
  { value: "medium", label: "Medium (51-200 employees)" },
  { value: "large", label: "Large (201-1000 employees)" },
  { value: "enterprise", label: "Enterprise (1000+ employees)" },
]

const saudiCities = ["Riyadh", "Jeddah", "Dammam", "Mecca", "Medina", "Khobar", "Tabuk", "Buraidah", "Khamis Mushait", "Hail", "Jubail", "Abha", "Yanbu", "Other"]
const blockedDomains = new Set(["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com", "icloud.com", "live.com", "msn.com"])

const getEmailError = (value: string) => {
  const trimmed = value.trim()
  if (!trimmed) return ""
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) return "Please enter a valid work email address."
  const domain = trimmed.split("@")[1]?.toLowerCase()
  if (blockedDomains.has(domain)) return "Please use your company email address."
  return ""
}

export default function Signup() {
  const navigate = useNavigate()
  const { signup } = useAuth()
  const [currentStep, setCurrentStep] = useState(1)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [emailError, setEmailError] = useState("")
  const [profilePicture, setProfilePicture] = useState<File | null>(null)
  const [acceptedTerms, setAcceptedTerms] = useState(true)
  const [formData, setFormData] = useState<SignupData>({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    title: "",
    organizationName: "",
    industry: "",
    organizationSize: "",
    country: "Saudi Arabia",
    city: "",
  })

  const handleInputChange = (field: keyof SignupData, value: string) => {
    setFormData((previous) => ({ ...previous, [field]: value }))
    if (field === "email") setEmailError(getEmailError(value))
  }

  const validateStep = () => {
    if (currentStep === 1) {
      const emailIssue = getEmailError(formData.email)
      setEmailError(emailIssue)
      if (!formData.firstName.trim() || !formData.lastName.trim() || !formData.email.trim() || !formData.title.trim()) return "Complete your name, job title, and work email."
      if (emailIssue) return ""
      return ""
    }
    if (currentStep === 2) {
      if (!formData.organizationName.trim() || !formData.industry || !formData.organizationSize || !formData.city) return "Complete the organization details."
      return ""
    }
    if (formData.password.length < 8 || !/[a-z]/.test(formData.password) || !/[0-9]/.test(formData.password)) return "Password must be at least 8 characters with a lowercase letter and a number."
    if (formData.password !== confirmPassword) return "Passwords do not match."
    if (!acceptedTerms) return "Accept the terms and privacy policy to continue."
    return ""
  }

  const handleNext = () => {
    const issue = validateStep()
    if (issue) {
      setError(issue)
      return
    }
    setError("")
    setCurrentStep((step) => Math.min(3, step + 1))
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    const issue = validateStep()
    if (issue) {
      setError(issue)
      return
    }

    setError("")
    setIsLoading(true)

    try {
      const signupResponse = await signup({ ...formData, email: formData.email.trim().toLowerCase() })

      if (profilePicture) {
        const reader = new FileReader()
        reader.onload = () => {
          localStorage.setItem("pendingProfilePicture", reader.result as string)
          localStorage.setItem("pendingProfilePictureType", profilePicture.type)
        }
        reader.readAsDataURL(profilePicture)
      }

      if (signupResponse && typeof signupResponse === "object" && signupResponse.requiresOTPVerification) {
        navigate(`/verify-otp?purpose=signup_verify&email=${encodeURIComponent(signupResponse.email || formData.email)}`)
      } else {
        navigate("/dashboard")
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Signup failed")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthScaffold
      eyebrow="Get started"
      steps={[
        { label: "Work email", detail: "Use your company domain" },
        { label: "Organization", detail: "Create or match workspace" },
        { label: "Verify", detail: "Confirm email and security" },
      ]}
      activeStep={currentStep}
      wide
      contextTitle="What happens next"
      contextItems={[
        { icon: Mail, title: "Verify your work email", body: "A one-time code confirms your account and activates the existing SuperTokens verification path.", tone: "teal" },
        { icon: Building2, title: "Create or match organization", body: "Your company domain helps locate or create the correct organization workspace.", tone: "amber" },
        { icon: User, title: "Invite teammates after signup", body: "Organization administrators can add members once the workspace is active.", tone: "blue" },
      ]}
    >
      <AuthCard>
        <AuthHeading title="Create organization account" subtitle="Set up a verified workspace for your manufacturing team." />
        {error ? <AuthAlert tone="error">{error}</AuthAlert> : null}

        <form onSubmit={handleSubmit} className="grid gap-5">
          {currentStep === 1 ? (
            <div className="grid gap-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <TextField icon={User} label="First name" value={formData.firstName} onChange={(value) => handleInputChange("firstName", value)} placeholder="Ahmed" />
                <TextField icon={User} label="Last name" value={formData.lastName} onChange={(value) => handleInputChange("lastName", value)} placeholder="Al-Faisal" />
              </div>
              <TextField icon={Mail} label="Work email" value={formData.email} onChange={(value) => handleInputChange("email", value)} placeholder="name@company.com" type="email" hint="Use your company domain" error={emailError} />
              <TextField icon={BriefcaseBusiness} label="Job title" value={formData.title} onChange={(value) => handleInputChange("title", value)} placeholder="Operations Manager" />
            </div>
          ) : null}

          {currentStep === 2 ? (
            <div className="grid gap-4">
              <TextField icon={Building2} label="Organization name" value={formData.organizationName} onChange={(value) => handleInputChange("organizationName", value)} placeholder="Enter your organization name" hint="We match existing organizations using your verified email domain where possible." />
              <div className="grid gap-4 sm:grid-cols-2">
                <SelectField label="Industry" value={formData.industry} onChange={(value) => handleInputChange("industry", value)} options={industries.map((industry) => ({ value: industry, label: industry }))} />
                <SelectField label="Organization size" value={formData.organizationSize} onChange={(value) => handleInputChange("organizationSize", value)} options={organizationSizes} />
              </div>
              <SelectField label="City" value={formData.city} onChange={(value) => handleInputChange("city", value)} options={saudiCities.map((city) => ({ value: city, label: city }))} />
            </div>
          ) : null}

          {currentStep === 3 ? (
            <div className="grid gap-4">
              <div className="rounded-[5px] border border-[var(--peer-line)] bg-white/50 p-4">
                <p className="mb-3 text-xs font-bold text-[var(--peer-ink)]">Optional profile photo</p>
                <ProfilePictureEditor onImageUpload={async (file) => setProfilePicture(file)} size="md" />
              </div>
              <PasswordField label="Password" value={formData.password} onChange={(value) => handleInputChange("password", value)} show={showPassword} onToggle={() => setShowPassword((value) => !value)} />
              <PasswordRequirements password={formData.password} />
              <PasswordField label="Confirm password" value={confirmPassword} onChange={setConfirmPassword} show={showConfirmPassword} onToggle={() => setShowConfirmPassword((value) => !value)} />
              <label className="flex items-start gap-2 text-xs text-[var(--peer-muted)]">
                <input type="checkbox" checked={acceptedTerms} onChange={(event) => setAcceptedTerms(event.target.checked)} className="mt-0.5 size-4 accent-[var(--peer-blue)]" />
                <span>I agree to the terms and privacy policy.</span>
              </label>
            </div>
          ) : null}

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-between">
            <Button type="button" variant="outline" onClick={() => currentStep === 1 ? navigate("/login") : setCurrentStep((step) => step - 1)} className="rounded-[5px]">
              <ArrowLeft className="size-4" />{currentStep === 1 ? "Sign in instead" : "Back"}
            </Button>
            {currentStep < 3 ? (
              <Button type="button" onClick={handleNext} className="rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
                Continue<ArrowRight className="size-4" />
              </Button>
            ) : (
              <Button type="submit" disabled={isLoading} className="rounded-[5px] bg-[var(--peer-blue)] text-white hover:bg-[#0f5ccc]">
                {isLoading ? <><Loader2 className="size-4 animate-spin" />Creating account...</> : <>Create account<ArrowRight className="size-4" /></>}
              </Button>
            )}
          </div>
        </form>

        <p className="mt-6 text-center text-sm text-[var(--peer-muted)]">
          Already have an account? <Link className="font-bold text-[var(--peer-blue)]" to="/login">Sign in</Link>
        </p>
      </AuthCard>
    </AuthScaffold>
  )
}

function TextField({ icon: Icon, label, value, onChange, placeholder, type = "text", hint, error }: { icon: typeof User; label: string; value: string; onChange: (value: string) => void; placeholder: string; type?: string; hint?: string; error?: string }) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <label className="text-xs font-bold text-[#07161d]">{label}</label>
        {hint ? <span className="text-right text-[10px] text-[var(--peer-muted)]">{hint}</span> : null}
      </div>
      <div className="relative">
        <Icon className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
        <Input type={type} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className={`h-12 rounded-[5px] bg-white/70 pl-11 ${error ? "border-[var(--peer-danger)]" : ""}`} required />
      </div>
      <FieldError message={error} />
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

function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: Array<{ value: string; label: string }> }) {
  return (
    <div>
      <label className="mb-2 block text-xs font-bold text-[#07161d]">{label}</label>
      <div className="relative">
        <MapPin className="pointer-events-none absolute left-3 top-1/2 size-5 -translate-y-1/2 text-[var(--peer-muted)]" />
        <select value={value} onChange={(event) => onChange(event.target.value)} className="h-12 w-full rounded-[5px] border border-[var(--peer-line)] bg-white/70 pl-11 pr-3 text-sm text-[var(--peer-ink)]" required>
          <option value="">Select {label.toLowerCase()}</option>
          {options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
      </div>
    </div>
  )
}

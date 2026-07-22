import { useCallback, useEffect, useState, type FormEvent, type ReactNode } from "react"
import {
  AlertCircle,
  BriefcaseBusiness,
  Building2,
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  Mail,
  MapPin,
  Plus,
  Save,
  ShieldCheck,
  UserRound,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/contexts/AuthContext"
import { buildApiUrl } from "@/config/environment"
import type { UpdateProfileData } from "@/types/auth"
import { ProfilePictureEditor } from "@/components/ui/ProfilePictureEditor"

interface EditProfilePanelProps {
  isOpen: boolean
  onClose: () => void
  onSave: () => void
  initialTab?: "profile" | "account"
}

const fieldClass = "mt-2 h-11 w-full border border-[var(--peer-line)] bg-white px-3 text-sm outline-none transition focus:border-[var(--peer-blue)] focus:ring-4 focus:ring-[rgba(23,105,223,.1)]"
const disabledFieldClass = `${fieldClass} cursor-not-allowed bg-[#f0efe9] text-[var(--peer-muted)] focus:ring-0`

function SectionCard({ icon, eyebrow, title, description, children }: { icon: ReactNode; eyebrow: string; title: string; description: string; children: ReactNode }) {
  return (
    <section className="border border-[var(--peer-line)] bg-white">
      <header className="flex items-start gap-4 border-b border-[var(--peer-line)] bg-[#f6f5f0] p-5">
        <span className="grid size-10 shrink-0 place-items-center border border-[#bad5cf] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]">{icon}</span>
        <div>
          <p className="peer-eyebrow">{eyebrow}</p>
          <h3 className="mt-1 font-display text-xl font-semibold text-[var(--peer-navy)]">{title}</h3>
          <p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">{description}</p>
        </div>
      </header>
      <div className="p-5">{children}</div>
    </section>
  )
}

function PasswordInput({ label, value, show, onChange, onToggle, placeholder }: { label: string; value: string; show: boolean; onChange: (value: string) => void; onToggle: () => void; placeholder: string }) {
  return (
    <label className="block text-xs font-bold text-[var(--peer-ink)]">
      {label}
      <span className="relative mt-2 block">
        <input type={show ? "text" : "password"} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className={`${fieldClass} mt-0 pr-11`} required />
        <button type="button" onClick={onToggle} className="absolute right-1 top-1/2 grid size-9 -translate-y-1/2 place-items-center text-[var(--peer-muted)] hover:text-[var(--peer-blue)]" aria-label={show ? `Hide ${label}` : `Show ${label}`}>
          {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
        </button>
      </span>
    </label>
  )
}

export function EditProfilePanel({ isOpen, onClose, onSave, initialTab = "profile" }: EditProfilePanelProps) {
  const { user, refreshProfile } = useAuth()
  const [activeTab, setActiveTab] = useState<"profile" | "account">(initialTab)
  const [profileLoading, setProfileLoading] = useState(false)
  const [emailLoading, setEmailLoading] = useState(false)
  const [passwordLoading, setPasswordLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [tagInput, setTagInput] = useState("")
  const [tagError, setTagError] = useState<string | null>(null)
  const [formData, setFormData] = useState<UpdateProfileData>({ firstName: "", lastName: "", title: "", location: "", expertiseTags: [] })
  const [emailForm, setEmailForm] = useState({ newEmail: "", password: "" })
  const [passwordForm, setPasswordForm] = useState({ currentPassword: "", newPassword: "", confirmPassword: "" })
  const [showPasswords, setShowPasswords] = useState({ current: false, new: false, confirm: false })

  useEffect(() => {
    if (!user || !isOpen) return
    setFormData({
      firstName: user.firstName || "",
      lastName: user.lastName || "",
      title: user.title || "",
      location: user.location || "",
      expertiseTags: user.expertiseTags || [],
    })
    setEmailForm({ newEmail: "", password: "" })
    setPasswordForm({ currentPassword: "", newPassword: "", confirmPassword: "" })
    setError(null)
    setFieldErrors({})
    setTagError(null)
    setSuccessMessage(null)
    setActiveTab(initialTab)
  }, [initialTab, isOpen, user])

  const clearMessages = () => { setError(null); setSuccessMessage(null) }

  const handleProfileSubmit = async (event: FormEvent) => {
    event.preventDefault()
    clearMessages()
    setProfileLoading(true)
    try {
      const response = await fetch(buildApiUrl("/api/v1/auth/profile"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(formData),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        if (response.status === 422 && Array.isArray(data.detail)) {
          const nextErrors: Record<string, string> = {}
          data.detail.forEach((item: { loc?: string[]; msg?: string }) => {
            const field = item.loc?.[item.loc.length - 1]
            if (field) nextErrors[field] = item.msg?.replace("Value error, ", "") || "Invalid value"
          })
          setFieldErrors(nextErrors)
        }
        throw new Error(typeof data.detail === "string" ? data.detail : "Please review the highlighted profile fields.")
      }
      await refreshProfile()
      onSave()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to update profile.")
    } finally {
      setProfileLoading(false)
    }
  }

  const handleAddTag = () => {
    const tag = tagInput.trim()
    if (!tag) return
    if (tag.length < 2 || tag.length > 30) { setTagError("Use 2–30 characters per expertise tag."); return }
    if (!/^[\w\s\-\u0600-\u06FF]+$/.test(tag)) { setTagError("Use letters, numbers, spaces, or hyphens only."); return }
    if (formData.expertiseTags?.includes(tag)) { setTagError("This expertise tag is already listed."); return }
    setFormData((current) => ({ ...current, expertiseTags: [...(current.expertiseTags || []), tag] }))
    setTagInput("")
    setTagError(null)
  }

  const getEmailDomain = (email: string) => email.includes("@") ? email.split("@").pop()?.trim().toLowerCase() || "" : ""
  const blockedDomains = new Set(["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com", "icloud.com", "live.com", "msn.com"])
  const currentDomain = getEmailDomain(user?.email || "")
  const newDomain = getEmailDomain(emailForm.newEmail)
  const emailDomainInvalid = Boolean(emailForm.newEmail && (blockedDomains.has(newDomain) || (currentDomain && newDomain && currentDomain !== newDomain)))

  const handleEmailUpdate = async (event: FormEvent) => {
    event.preventDefault()
    clearMessages()
    if (emailDomainInvalid) { setError(`Use an approved organization email${currentDomain ? ` ending in @${currentDomain}` : ""}.`); return }
    setEmailLoading(true)
    try {
      const response = await fetch(buildApiUrl("/api/v1/auth/email"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(emailForm),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(data.detail || "Failed to update email.")
      setEmailForm({ newEmail: "", password: "" })
      setSuccessMessage("Email address updated successfully.")
      await refreshProfile()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to update email.")
    } finally {
      setEmailLoading(false)
    }
  }

  const handlePasswordUpdate = async (event: FormEvent) => {
    event.preventDefault()
    clearMessages()
    if (passwordForm.newPassword.length < 8 || !/[a-z]/.test(passwordForm.newPassword) || !/[0-9]/.test(passwordForm.newPassword)) { setError("Use at least 8 characters with a lowercase letter and a number."); return }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) { setError("New passwords do not match."); return }
    setPasswordLoading(true)
    try {
      const response = await fetch(buildApiUrl("/api/v1/auth/password"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ currentPassword: passwordForm.currentPassword, newPassword: passwordForm.newPassword }),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(data.detail || "Failed to update password.")
      setPasswordForm({ currentPassword: "", newPassword: "", confirmPassword: "" })
      setSuccessMessage("Password updated successfully.")
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to update password.")
    } finally {
      setPasswordLoading(false)
    }
  }

  const handleProfilePictureUpload = useCallback(async (file: File) => {
    clearMessages()
    try {
      const body = new FormData()
      body.append("file", file)
      const response = await fetch(buildApiUrl("/api/v1/media/profile-picture"), { method: "POST", body, credentials: "include" })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(data.detail || "Failed to upload profile picture.")
      await refreshProfile()
      setSuccessMessage("Profile picture updated successfully.")
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to upload profile picture.")
    }
  }, [refreshProfile])

  if (!isOpen) return null
  const busy = profileLoading || emailLoading || passwordLoading

  return (
    <div className="fixed inset-0 z-50" role="dialog" aria-modal="true" aria-label={activeTab === "profile" ? "Edit profile" : "Password and security"}>
      <button type="button" aria-label="Close settings" className="absolute inset-0 cursor-default bg-[#061f2d]/55 backdrop-blur-[2px]" onClick={onClose} />
      <aside className="absolute inset-y-0 right-0 flex w-full max-w-[700px] flex-col border-l border-[var(--peer-line)] bg-[var(--peer-paper)] shadow-[-24px_0_70px_rgba(5,28,40,.22)]">
        <header className="border-b border-white/15 bg-[var(--peer-navy)] px-5 py-5 text-white sm:px-7">
          <div className="flex items-start justify-between gap-5">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#7fc9c0]">Account workspace</p>
              <h2 className="mt-2 font-display text-2xl font-semibold">Profile and security</h2>
              <p className="mt-1 max-w-lg text-xs leading-5 text-[#b8cbca]">Keep your contributor details accurate and manage access to your PeerLink account.</p>
            </div>
            <button type="button" onClick={onClose} disabled={busy} className="grid size-10 shrink-0 place-items-center border border-white/20 text-white hover:bg-white/10" aria-label="Close profile settings"><X className="size-5" /></button>
          </div>
        </header>

        <nav className="grid grid-cols-2 border-b border-[var(--peer-line)] bg-white" aria-label="Profile settings sections">
          <button type="button" onClick={() => { setActiveTab("profile"); clearMessages() }} className={`flex min-h-14 items-center justify-center gap-2 border-b-2 px-4 text-sm font-bold ${activeTab === "profile" ? "border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] text-[var(--peer-navy)]" : "border-transparent text-[var(--peer-muted)] hover:bg-[#f6f5f0]"}`}><UserRound className="size-4" />Edit profile</button>
          <button type="button" onClick={() => { setActiveTab("account"); clearMessages() }} className={`flex min-h-14 items-center justify-center gap-2 border-b-2 px-4 text-sm font-bold ${activeTab === "account" ? "border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] text-[var(--peer-navy)]" : "border-transparent text-[var(--peer-muted)] hover:bg-[#f6f5f0]"}`}><ShieldCheck className="size-4" />Password & security</button>
        </nav>

        <div className="flex-1 overflow-y-auto p-4 sm:p-7">
          {error ? <div className="mb-5 flex items-start gap-3 border-l-4 border-[var(--peer-danger)] bg-[#fff0ed] p-4 text-sm text-[#8e2f27]"><AlertCircle className="mt-0.5 size-4 shrink-0" />{error}</div> : null}
          {successMessage ? <div className="mb-5 flex items-start gap-3 border-l-4 border-[var(--peer-success)] bg-[#edf8f2] p-4 text-sm text-[#16634f]"><CheckCircle2 className="mt-0.5 size-4 shrink-0" />{successMessage}</div> : null}

          {activeTab === "profile" ? (
            <form onSubmit={handleProfileSubmit} className="grid gap-5">
              <SectionCard icon={<UserRound className="size-5" />} eyebrow="Public identity" title="Contributor profile" description="These details appear beside your discussions and submitted implementation stories.">
                <div className="grid gap-6 sm:grid-cols-[150px_1fr] sm:items-center">
                  <div className="border-r-0 border-[var(--peer-line)] sm:border-r sm:pr-6"><ProfilePictureEditor currentImageUrl={user?.profilePictureUrl || undefined} onImageUpload={handleProfilePictureUpload} size="lg" disabled={profileLoading} /></div>
                  <div><strong className="font-display text-lg text-[var(--peer-navy)]">{[formData.firstName, formData.lastName].filter(Boolean).join(" ") || "PeerLink member"}</strong><p className="mt-1 text-xs text-[var(--peer-muted)]">Upload a clear square image. Your profile photo is visible to members of the manufacturing network.</p></div>
                </div>
              </SectionCard>

              <section className="border border-[var(--peer-line)] bg-white p-5">
                <div className="grid gap-5 sm:grid-cols-2">
                  <label className="text-xs font-bold">First name *<input value={formData.firstName} onChange={(event) => { setFormData((current) => ({ ...current, firstName: event.target.value })); setFieldErrors((current) => ({ ...current, firstName: "" })) }} className={fieldClass} required />{fieldErrors.firstName ? <small className="mt-1 block text-[var(--peer-danger)]">{fieldErrors.firstName}</small> : null}</label>
                  <label className="text-xs font-bold">Last name *<input value={formData.lastName} onChange={(event) => { setFormData((current) => ({ ...current, lastName: event.target.value })); setFieldErrors((current) => ({ ...current, lastName: "" })) }} className={fieldClass} required />{fieldErrors.lastName ? <small className="mt-1 block text-[var(--peer-danger)]">{fieldErrors.lastName}</small> : null}</label>
                  <label className="text-xs font-bold"><span className="inline-flex items-center gap-2"><BriefcaseBusiness className="size-4 text-[var(--peer-teal)]" />Job title</span><input value={formData.title} onChange={(event) => setFormData((current) => ({ ...current, title: event.target.value }))} placeholder="Manufacturing Engineer" className={fieldClass} /></label>
                  <label className="text-xs font-bold"><span className="inline-flex items-center gap-2"><MapPin className="size-4 text-[var(--peer-teal)]" />Location</span><input value={formData.location} onChange={(event) => setFormData((current) => ({ ...current, location: event.target.value }))} placeholder="Riyadh, Saudi Arabia" className={fieldClass} /></label>
                  <label className="text-xs font-bold"><span className="inline-flex items-center gap-2"><Building2 className="size-4 text-[var(--peer-teal)]" />Organization</span><input value={user?.company || ""} disabled className={disabledFieldClass} /></label>
                  <label className="text-xs font-bold">Industry sector<input value={user?.industrySector || ""} disabled className={disabledFieldClass} /></label>
                </div>
              </section>

              <SectionCard icon={<Plus className="size-5" />} eyebrow="Discoverability" title="Expertise tags" description="Add practical topics that help peers find the right person for a discussion.">
                <div className="flex gap-2"><input value={tagInput} onChange={(event) => { setTagInput(event.target.value); setTagError(null) }} onKeyDown={(event) => { if (event.key === "Enter") { event.preventDefault(); handleAddTag() } }} placeholder="For example, Industrial IoT" className={`${fieldClass} mt-0`} /><Button type="button" variant="outline" onClick={handleAddTag} className="h-11 rounded-none border-[var(--peer-line)]"><Plus className="size-4" />Add</Button></div>
                {tagError ? <p className="mt-2 text-xs text-[var(--peer-danger)]">{tagError}</p> : null}
                <div className="mt-4 flex flex-wrap gap-2">{formData.expertiseTags?.length ? formData.expertiseTags.map((tag) => <span key={tag} className="inline-flex items-center gap-2 border border-[#bad5cf] bg-[var(--peer-teal-soft)] px-3 py-1.5 text-xs font-semibold text-[var(--peer-teal)]">{tag}<button type="button" onClick={() => setFormData((current) => ({ ...current, expertiseTags: current.expertiseTags?.filter((item) => item !== tag) || [] }))} aria-label={`Remove ${tag}`}><X className="size-3.5" /></button></span>) : <p className="text-xs text-[var(--peer-muted)]">No expertise tags added yet.</p>}</div>
              </SectionCard>

              <div className="sticky bottom-0 flex flex-wrap justify-end gap-2 border border-[var(--peer-line)] bg-[rgba(255,255,255,.96)] p-4 backdrop-blur"><Button type="button" variant="outline" onClick={onClose} className="rounded-none border-[var(--peer-line)]">Cancel</Button><Button type="submit" disabled={profileLoading} className="rounded-none bg-[var(--peer-teal)] text-white hover:bg-[#17636a]">{profileLoading ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}{profileLoading ? "Saving profile..." : "Save profile"}</Button></div>
            </form>
          ) : (
            <div className="grid gap-5">
              <div className="border-l-4 border-[var(--peer-blue)] bg-[#edf4ff] p-4 text-sm text-[var(--peer-navy)]"><strong className="block">Security settings</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">Changes require your current password. Your active session remains protected by PeerLink device verification.</span></div>

              <SectionCard icon={<Mail className="size-5" />} eyebrow="Account identity" title="Change email address" description={`PeerLink accepts approved work email addresses${currentDomain ? ` from @${currentDomain}` : ""}.`}>
                <form onSubmit={handleEmailUpdate} className="grid gap-4">
                  <label className="text-xs font-bold">Current email<input type="email" value={user?.email || ""} disabled className={disabledFieldClass} /></label>
                  <label className="text-xs font-bold">New work email<input type="email" value={emailForm.newEmail} onChange={(event) => setEmailForm((current) => ({ ...current, newEmail: event.target.value }))} placeholder={currentDomain ? `name@${currentDomain}` : "name@company.com"} className={`${fieldClass} ${emailDomainInvalid ? "border-[var(--peer-danger)]" : ""}`} required />{emailDomainInvalid ? <small className="mt-1 block text-[var(--peer-danger)]">Use your approved organization email domain.</small> : <small className="mt-1 block font-normal text-[var(--peer-muted)]">Personal email services are not accepted.</small>}</label>
                  <PasswordInput label="Current password" value={emailForm.password} show={showPasswords.current} onChange={(value) => setEmailForm((current) => ({ ...current, password: value }))} onToggle={() => setShowPasswords((current) => ({ ...current, current: !current.current }))} placeholder="Confirm your identity" />
                  <Button type="submit" disabled={emailLoading || emailDomainInvalid} className="justify-self-end rounded-none bg-[var(--peer-navy)] text-white">{emailLoading ? <Loader2 className="size-4 animate-spin" /> : <Mail className="size-4" />}{emailLoading ? "Updating email..." : "Update email"}</Button>
                </form>
              </SectionCard>

              <SectionCard icon={<KeyRound className="size-5" />} eyebrow="Access protection" title="Change password" description="Use a password that is unique to PeerLink and difficult to guess.">
                <form onSubmit={handlePasswordUpdate} className="grid gap-4">
                  <PasswordInput label="Current password" value={passwordForm.currentPassword} show={showPasswords.current} onChange={(value) => setPasswordForm((current) => ({ ...current, currentPassword: value }))} onToggle={() => setShowPasswords((current) => ({ ...current, current: !current.current }))} placeholder="Enter current password" />
                  <div className="grid gap-4 sm:grid-cols-2"><PasswordInput label="New password" value={passwordForm.newPassword} show={showPasswords.new} onChange={(value) => setPasswordForm((current) => ({ ...current, newPassword: value }))} onToggle={() => setShowPasswords((current) => ({ ...current, new: !current.new }))} placeholder="Create new password" /><PasswordInput label="Confirm password" value={passwordForm.confirmPassword} show={showPasswords.confirm} onChange={(value) => setPasswordForm((current) => ({ ...current, confirmPassword: value }))} onToggle={() => setShowPasswords((current) => ({ ...current, confirm: !current.confirm }))} placeholder="Repeat new password" /></div>
                  <div className="grid gap-2 border border-[var(--peer-line)] bg-[#f6f5f0] p-4 text-xs text-[var(--peer-muted)]"><span className="inline-flex items-center gap-2"><ShieldCheck className="size-4 text-[var(--peer-teal)]" />At least 8 characters</span><span className="inline-flex items-center gap-2"><ShieldCheck className="size-4 text-[var(--peer-teal)]" />Include a lowercase letter and a number</span></div>
                  <Button type="submit" disabled={passwordLoading} className="justify-self-end rounded-none bg-[var(--peer-teal)] text-white hover:bg-[#17636a]">{passwordLoading ? <Loader2 className="size-4 animate-spin" /> : <KeyRound className="size-4" />}{passwordLoading ? "Updating password..." : "Update password"}</Button>
                </form>
              </SectionCard>
            </div>
          )}
        </div>
      </aside>
    </div>
  )
}

import { useEffect, useMemo, useRef, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  ArrowLeft,
  ArrowRight,
  BadgeCheck,
  Building2,
  Check,
  CheckCircle2,
  Clock3,
  CloudCheck,
  FileImage,
  FileVideo,
  Loader2,
  MapPin,
  Save,
  Send,
  ShieldCheck,
  UploadCloud,
  UserRound,
  X,
} from "lucide-react"
import { buildApiUrl } from "@/config/environment"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useAuth } from "@/contexts/AuthContext"
import LocationPicker from "@/components/LocationPicker"

interface SimpleUseCaseForm {
  organization: string
  site: string
  city: string
  submitter: string
  jobTitle: string
  email: string
  title: string
  problem: string
  technology: string
  budgetRange: string
  budgetExact: string
  outcomes: string
  challenges: string
  category: string
  latitude: number
  longitude: number
}

interface ExistingUseCase {
  title?: string
  category?: string
  factory_name?: string
  region?: string
  location?: { lat?: number; lng?: number }
  contact_person?: string
  contact_title?: string
  executive_summary?: string
  problem?: string
  technology?: string
  budget?: string
  outcomes?: string
  challenges?: string
  business_challenge?: {
    industry_context?: string
    specific_problems?: string[]
  }
  solution_details?: {
    technology_components?: Array<string | { component?: string; details?: string }>
  }
  implementation_details?: { total_budget?: string }
  results?: {
    quantitative_metrics?: Array<{ metric?: string; improvement?: string; current?: string }>
    qualitative_impacts?: string[]
  }
  challenges_and_solutions?: Array<{ challenge?: string; description?: string; solution?: string; outcome?: string }>
  images?: string[]
}

const CITIES = [
  "Riyadh", "Jeddah", "Makkah", "Madinah", "Dammam", "Khobar", "Dhahran", "Jubail", "Yanbu", "Tabuk", "Taif", "Abha", "Hail", "Jizan", "Najran", "Other",
]

const BUDGETS = [
  "Below SAR 50,000",
  "SAR 50,000–250,000",
  "SAR 250,000–1 million",
  "Above SAR 1 million",
  "Unknown",
  "Prefer not to disclose",
]

const CATEGORIES = [
  "Quality Control", "Predictive Maintenance", "Factory Automation", "Artificial Intelligence", "Sustainability", "Process Optimization", "Supply Chain", "Innovation & R&D", "Training & Safety", "Energy Efficiency",
]

const CITY_COORDINATES: Record<string, [number, number]> = {
  Riyadh: [24.7136, 46.6753], Jeddah: [21.4858, 39.1925], Makkah: [21.3891, 39.8579], Madinah: [24.5247, 39.5692], Dammam: [26.4207, 50.0888], Khobar: [26.2172, 50.1971], Dhahran: [26.2361, 50.0393], Jubail: [27.0174, 49.6225], Yanbu: [24.0895, 38.0618], Tabuk: [28.3838, 36.5550], Taif: [21.2703, 40.4158], Abha: [18.2164, 42.5053], Hail: [27.5114, 41.7208], Jizan: [16.8892, 42.5511], Najran: [17.5650, 44.2289], Other: [24.7136, 46.6753],
}

const EMPTY_FORM: SimpleUseCaseForm = {
  organization: "",
  site: "",
  city: "Riyadh",
  submitter: "",
  jobTitle: "",
  email: "",
  title: "",
  problem: "",
  technology: "",
  budgetRange: "Unknown",
  budgetExact: "",
  outcomes: "",
  challenges: "",
  category: "Process Optimization",
  latitude: 24.7136,
  longitude: 46.6753,
}

const trimTo = (value: string, max: number) => value.trim().slice(0, max)
const hasDangerousContent = (value: string) => /<\s*script|javascript\s*:|on(?:error|load|click)\s*=|\.\.\/|\x00/i.test(value)

async function apiError(response: Response) {
  const body = await response.json().catch(() => null)
  if (Array.isArray(body?.detail)) return body.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join("; ") || "The submission could not be saved."
  return body?.detail || body?.message || `The request failed (${response.status}).`
}

function FieldError({ children }: { children?: string }) {
  return children ? <p className="mt-1 text-xs font-semibold text-[var(--peer-danger)]">{children}</p> : null
}

function QuestionCard({ number, label, help, prompts, required, children }: { number: string; label: string; help: string; prompts?: string[]; required?: boolean; children: React.ReactNode }) {
  return (
    <section className="border border-[var(--peer-line)] bg-white p-5">
      <div className="mb-2 flex items-center justify-between gap-3 text-[10px] font-bold uppercase tracking-[.12em]">
        <span className="text-[var(--peer-teal)]">Question {number}</span>
        <span className="text-[var(--peer-muted)]">{required ? "Required" : "Optional"}</span>
      </div>
      <label className="font-display text-base font-semibold leading-6 text-[var(--peer-ink)]">{label}</label>
      <p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">{help}</p>
      {prompts?.length ? (
        <div className="my-3 border-l-2 border-[#bad5cf] bg-[var(--peer-teal-soft)] px-4 py-3">
          <p className="text-[10px] font-bold uppercase tracking-[.12em] text-[var(--peer-teal)]">You could include</p>
          <ul className="mt-1.5 grid gap-1 pl-4 text-xs leading-5 text-[var(--peer-muted)]">
            {prompts.map((prompt) => <li key={prompt} className="list-disc">{prompt}</li>)}
          </ul>
        </div>
      ) : <div className="mb-3" />}
      {children}
    </section>
  )
}

export default function SubmitUseCase() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { user, organization } = useAuth()
  const editId = searchParams.get("edit")
  const initialDraftId = searchParams.get("draft")
  const storageKey = `peerlink_simple_usecase_${editId || initialDraftId || "new"}`
  const [step, setStep] = useState(1)
  const [form, setForm] = useState<SimpleUseCaseForm>(EMPTY_FORM)
  const [files, setFiles] = useState<File[]>([])
  const [existingImages, setExistingImages] = useState<string[]>([])
  const [draftId, setDraftId] = useState<string | null>(initialDraftId)
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved" | "failed">("idle")
  const [submitting, setSubmitting] = useState(false)
  const [loading, setLoading] = useState(Boolean(editId || initialDraftId))
  const [submitted, setSubmitted] = useState(false)
  const [confirmed, setConfirmed] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const hydrated = useRef(false)
  const autosaveTimer = useRef<number | null>(null)

  const update = (field: keyof SimpleUseCaseForm, value: string | number) => {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: "" }))
  }

  const updateCity = (city: string) => {
    const coords = CITY_COORDINATES[city]
    setForm((current) => ({
      ...current,
      city,
      latitude: coords?.[0] ?? current.latitude,
      longitude: coords?.[1] ?? current.longitude,
    }))
    setErrors((current) => ({ ...current, city: "" }))
  }

  useEffect(() => {
    if (hydrated.current) return
    const local = localStorage.getItem(storageKey)
    if (local && !editId && !initialDraftId) {
      try {
        const saved = JSON.parse(local)
        if (saved.form) setForm((current) => ({ ...current, ...saved.form }))
        if (saved.step) setStep(Math.min(3, Math.max(1, saved.step)))
      } catch { /* Ignore an invalid local draft. */ }
    } else {
      const name = [user?.firstName, user?.lastName].filter(Boolean).join(" ")
      const city = organization?.city || user?.location || "Riyadh"
      const coords = CITY_COORDINATES[city]
      setForm((current) => ({
        ...current,
        organization: organization?.name || user?.company || "",
        city,
        latitude: coords?.[0] ?? current.latitude,
        longitude: coords?.[1] ?? current.longitude,
        submitter: name,
        jobTitle: user?.title || "",
        email: user?.email || "",
      }))
    }
    hydrated.current = true
  }, [editId, initialDraftId, organization, storageKey, user])


  useEffect(() => {
    if (!hydrated.current || editId) return
    setSaveState("saving")
    if (autosaveTimer.current) window.clearTimeout(autosaveTimer.current)
    autosaveTimer.current = window.setTimeout(() => {
      try {
        localStorage.setItem(storageKey, JSON.stringify({ form, step, savedAt: Date.now() }))
        setSaveState("saved")
      } catch { setSaveState("failed") }
    }, 500)
    return () => { if (autosaveTimer.current) window.clearTimeout(autosaveTimer.current) }
  }, [editId, form, step, storageKey])

  const restoreFromBackend = (data: ExistingUseCase & Record<string, unknown>) => {
    const components = (data.solution_details?.technology_components || []).map((item) => typeof item === "string" ? item : [item.component, item.details].filter(Boolean).join(": ")).filter(Boolean)
    const outcomes = data.results?.qualitative_impacts?.join("\n") || data.results?.quantitative_metrics?.map((item) => [item.metric, item.improvement || item.current].filter(Boolean).join(": ")).join("\n") || data.executive_summary || ""
    const challenges = data.challenges_and_solutions?.map((item) => item.description || item.challenge).filter(Boolean).join("\n") || ""
    setForm((current) => ({
      ...current,
      title: data.title || "",
      category: data.category || "Process Optimization",
      site: data.factory_name || "",
      city: data.region || current.city,
      latitude: data.location?.lat ?? current.latitude,
      longitude: data.location?.lng ?? current.longitude,
      submitter: data.contact_person || current.submitter,
      jobTitle: data.contact_title || current.jobTitle,
      problem: data.problem || data.business_challenge?.specific_problems?.join("\n") || data.business_challenge?.industry_context || "",
      technology: data.technology || components.join("\n"),
      budgetRange: data.budget || data.implementation_details?.total_budget || "Unknown",
      outcomes: data.outcomes || outcomes,
      challenges: data.challenges || challenges,
    }))
    setExistingImages(Array.isArray(data.images) ? data.images : [])
  }

  useEffect(() => {
    if (!editId && !initialDraftId) { setLoading(false); return }
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const path = editId ? `/api/v1/use-cases/by-id/${editId}` : `/api/v1/use-cases/drafts/${initialDraftId}`
        const response = await fetch(buildApiUrl(path), { credentials: "include" })
        if (!response.ok) throw new Error(await apiError(response))
        const data = await response.json()
        if (editId) restoreFromBackend(data)
        else {
          setDraftId(initialDraftId)
          setStep(Math.min(3, Number(data.currentStep || data.current_step || 1)))
          setForm((current) => ({
            ...current,
            title: data.title || "",
            category: data.category || "Process Optimization",
            site: data.factoryName || "",
            city: data.city || current.city,
            latitude: data.latitude ?? current.latitude,
            longitude: data.longitude ?? current.longitude,
            submitter: data.contactPerson || current.submitter,
            jobTitle: data.contactTitle || current.jobTitle,
            problem: data.specificProblems?.join("\n") || data.industryContext || "",
            technology: data.technologyComponents?.join("\n") || data.methodology || "",
            budgetRange: data.totalBudget || "Unknown",
            outcomes: data.qualitativeImpacts?.join("\n") || data.description || "",
            challenges: data.challengesSolutions?.map((item: { description?: string; challenge?: string }) => item.description || item.challenge).filter(Boolean).join("\n") || "",
          }))
          setExistingImages(data.images || [])
        }
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : "The saved use case could not be loaded.")
      } finally { setLoading(false) }
    }
    void load()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editId, initialDraftId])

  const draftPayload = () => ({
    draftId: draftId || undefined,
    currentStep: step,
    title: form.title.trim() || null,
    subtitle: trimTo(form.technology, 150) || null,
    description: form.outcomes.trim() || null,
    category: form.category || "Process Optimization",
    factoryName: form.site.trim() || null,
    city: form.city || null,
    latitude: form.latitude,
    longitude: form.longitude,
    industryContext: form.problem.trim() || null,
    specificProblems: form.problem.trim() ? [trimTo(form.problem, 500)] : null,
    financialLoss: form.budgetExact.trim() || form.budgetRange || null,
    selectionCriteria: form.technology.trim() ? [trimTo(form.technology, 500)] : null,
    technologyComponents: form.technology.trim() ? [trimTo(form.technology, 500)] : null,
    totalBudget: form.budgetExact.trim() || form.budgetRange || null,
    methodology: form.technology.trim() || null,
    qualitativeImpacts: form.outcomes.trim() ? [trimTo(form.outcomes, 500)] : null,
    challengesSolutions: form.challenges.trim() ? [{ challenge: "Implementation challenges", description: trimTo(form.challenges, 1000), solution: "Response described by the contributor", outcome: "Captured for publication review" }] : null,
    contactPerson: form.submitter.trim() || null,
    contactTitle: form.jobTitle.trim() || null,
    images: existingImages.length ? existingImages : null,
  })

  const saveDraft = async (quiet = false) => {
    if (editId) {
      localStorage.setItem(storageKey, JSON.stringify({ form, step, savedAt: Date.now() }))
      setSaveState("saved")
      return true
    }
    setSaveState("saving")
    if (!quiet) setError(null)
    try {
      const response = await fetch(buildApiUrl("/api/v1/use-cases/drafts"), {
        method: "POST", headers: { "Content-Type": "application/json" }, credentials: "include", body: JSON.stringify(draftPayload()),
      })
      if (!response.ok) throw new Error(await apiError(response))
      const data = await response.json()
      const id = data.draft_id || data.id
      if (id) {
        setDraftId(id)
        if (!initialDraftId) window.history.replaceState({}, "", `/submit?draft=${id}`)
      }
      setSaveState("saved")
      return true
    } catch (reason) {
      setSaveState("failed")
      if (!quiet) setError(reason instanceof Error ? reason.message : "Draft saving failed.")
      return false
    }
  }

  const validateStep = (targetStep = step) => {
    const nextErrors: Record<string, string> = {}
    if (targetStep === 1) {
      if (!form.organization.trim()) nextErrors.organization = "Organization information is required."
      if (form.site.trim().length < 2) nextErrors.site = "Enter the factory or site name."
      if (!form.city) nextErrors.city = "Select a city."
      if (form.submitter.trim().length < 2) nextErrors.submitter = "Enter the contributor name."
      if (!/^\S+@\S+\.\S+$/.test(form.email)) nextErrors.email = "Enter a valid contact email."
    }
    if (targetStep === 2) {
      if (form.title.trim().length < 10) nextErrors.title = "Use at least 10 characters for the title."
      if (form.problem.trim().length < 50) nextErrors.problem = "Give a little more context (at least 50 characters)."
      if (form.technology.trim().length < 20) nextErrors.technology = "Describe the technology or approach in at least 20 characters."
      if (form.outcomes.trim().length < 20) nextErrors.outcomes = "Describe the observed outcome in at least 20 characters."
      if (form.challenges.trim() && form.challenges.trim().length < 20) nextErrors.challenges = "Add a little more detail, or leave challenges empty."
    }
    if (targetStep === 3) {
      if (!Number.isFinite(form.latitude) || form.latitude < -90 || form.latitude > 90) nextErrors.latitude = "Enter a latitude between -90 and 90."
      if (!Number.isFinite(form.longitude) || form.longitude < -180 || form.longitude > 180) nextErrors.longitude = "Enter a longitude between -180 and 180."
    }
    Object.entries(form).forEach(([key, value]) => { if (typeof value === "string" && hasDangerousContent(value)) nextErrors[key] = "This field contains a disallowed pattern." })
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const goNext = async () => {
    if (!validateStep()) return
    await saveDraft(true)
    setStep((current) => Math.min(3, current + 1))
    window.scrollTo({ top: 0, behavior: "smooth" })
  }

  const onFiles = (selected: FileList | null) => {
    if (!selected) return
    const accepted = Array.from(selected).filter((file) => ["image/jpeg", "image/png", "image/webp", "video/mp4", "video/webm"].includes(file.type))
    const withinLimits = accepted.filter((file) => file.size <= (file.type.startsWith("video/") ? 50 : 5) * 1024 * 1024)
    setFiles((current) => [...current, ...withinLimits].slice(0, 10))
    if (accepted.length !== selected.length || withinLimits.length !== accepted.length) setError("Some files were skipped. Use JPEG, PNG, WebP, MP4 or WebM; images are limited to 5 MB and videos to 50 MB.")
  }

  const finalPayload = () => {
    const problem = trimTo(form.problem, 500)
    const technology = trimTo(form.technology, 500)
    const budget = trimTo(form.budgetExact.trim() ? `Approx. ${form.budgetExact.trim()}` : form.budgetRange || "Unknown", 120)
    const challengeProvided = Boolean(form.challenges.trim())
    const challenge = challengeProvided ? trimTo(form.challenges, 1000) : "No implementation challenges were shared by the contributor."
    return {
      title: trimTo(form.title, 100),
      subtitle: trimTo(form.technology, 150),
      description: trimTo(`Problem: ${form.problem}\n\nOutcome: ${form.outcomes}`, 5000),
      category: form.category,
      factoryName: trimTo(form.site, 80),
      problem: trimTo(form.problem, 5000),
      technology: trimTo(form.technology, 5000),
      budget,
      outcomes: trimTo(form.outcomes, 5000),
      challenges: challengeProvided ? trimTo(form.challenges, 2000) : undefined,
      city: trimTo(form.city, 50),
      latitude: form.latitude,
      longitude: form.longitude,
      industryContext: trimTo(form.problem, 5000),
      specificProblems: [problem, problem],
      financialLoss: budget,
      selectionCriteria: [technology, technology],
      selectedVendor: "Not specified",
      technologyComponents: [technology],
      implementationTime: "Not specified",
      totalBudget: budget,
      methodology: trimTo(form.technology, 5000),
      quantitativeResults: [],
      qualitativeImpacts: [trimTo(form.outcomes, 500)],
      challengesSolutions: [{
        challenge: challengeProvided ? "Implementation challenges" : "No challenges shared",
        description: challenge,
        solution: challengeProvided ? "The contributor documented the implementation response for PeerLink review." : "No specific response was required or provided.",
        outcome: challengeProvided ? "The experience was captured for peer learning." : "No challenge outcome was provided.",
      }],
      contactPerson: trimTo(form.submitter, 120),
      contactTitle: trimTo(form.jobTitle || "Contributor", 120),
      images: existingImages,
      industryTags: undefined,
      technologyTags: undefined,
    }
  }

  const submit = async () => {
    if (!validateStep(1)) { setStep(1); return }
    if (!validateStep(2)) { setStep(2); return }
    if (!validateStep(3)) { setStep(3); return }
    if (!confirmed) { setError("Confirm that you are authorized to share this information."); return }
    setSubmitting(true)
    setError(null)
    try {
      const response = await fetch(buildApiUrl(editId ? `/api/v1/use-cases/${editId}` : "/api/v1/use-cases"), {
        method: editId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, credentials: "include", body: JSON.stringify(finalPayload()),
      })
      if (!response.ok) throw new Error(await apiError(response))
      const result = await response.json()
      const useCaseId = result.id || result._id || editId
      if (files.length && useCaseId) {
        const body = new window.FormData()
        files.forEach((file) => body.append("files", file))
        body.append("usecase_id", String(useCaseId))
        const mediaResponse = await fetch(buildApiUrl("/api/v1/media/usecase-media"), { method: "POST", credentials: "include", body })
        if (!mediaResponse.ok) throw new Error(`The use case was saved, but attachments failed: ${await apiError(mediaResponse)}`)
      }
      if (draftId) await fetch(buildApiUrl(`/api/v1/use-cases/drafts/${draftId}`), { method: "DELETE", credentials: "include" }).catch(() => undefined)
      localStorage.removeItem(storageKey)
      setSubmitted(true)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The use case could not be submitted.")
    } finally { setSubmitting(false) }
  }

  const informationProvided = useMemo(() => [form.problem && "problem", form.technology && "technology", form.budgetRange && "budget", form.outcomes && "outcomes", form.challenges && "challenges"].filter(Boolean).join(", "), [form])

  if (loading) return <main className="grid min-h-[65vh] place-items-center"><div className="flex items-center gap-3 text-sm text-[var(--peer-muted)]"><Loader2 className="size-5 animate-spin text-[var(--peer-teal)]" />Loading saved use case…</div></main>

  if (submitted) return (
    <main className="mx-auto grid min-h-[70vh] max-w-2xl place-items-center px-4 py-12">
      <section className="peer-panel w-full p-8 text-center">
        <span className="mx-auto grid size-16 place-items-center rounded-full bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><CheckCircle2 className="size-8" /></span>
        <p className="peer-eyebrow mt-6">Submission complete</p>
        <h1 className="mt-2 font-display text-3xl font-semibold">{editId ? "Use case updated" : "Use case submitted for review"}</h1>
        <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-[var(--peer-muted)]">Your information is safe. PeerLink can now review and organize the story for publication without asking you to complete a technical report.</p>
        <div className="mt-7 flex flex-wrap justify-center gap-2"><Button onClick={() => navigate("/usecases")} className="rounded-none bg-[var(--peer-navy)] text-white">Back to library</Button></div>
      </section>
    </main>
  )

  return (
    <main className="mx-auto w-full max-w-[1430px] px-4 py-7 md:px-8 md:py-10 xl:px-14">
      <header className="mb-7 flex flex-wrap items-start justify-between gap-5">
        <div>
          <p className="peer-eyebrow">Simplified submission</p>
          <h1 className="mt-2 max-w-3xl font-display text-3xl font-semibold tracking-[-.04em] sm:text-4xl">{editId ? "Update the use case in three simple steps." : "Share a use case in three simple steps."}</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--peer-muted)]">Tell peers what was done without completing a technical report. Your progress is saved while you work.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="inline-flex min-h-8 items-center gap-2 border border-[var(--peer-line)] bg-white px-3 text-xs font-semibold text-[var(--peer-muted)]"><Clock3 className="size-4 text-[var(--peer-teal)]" />About 5–10 minutes</span>
            <span className="inline-flex min-h-8 items-center gap-2 border border-[var(--peer-line)] bg-white px-3 text-xs font-semibold text-[var(--peer-muted)]"><CloudCheck className="size-4 text-[var(--peer-teal)]" />{saveState === "saving" ? "Saving…" : saveState === "failed" ? "Local save failed" : "Automatic draft saving"}</span>
            <span className="inline-flex min-h-8 items-center gap-2 border border-[var(--peer-line)] bg-white px-3 text-xs font-semibold text-[var(--peer-muted)]"><ShieldCheck className="size-4 text-[var(--peer-teal)]" />Reviewed before publication</span>
          </div>
        </div>
        <div className="flex gap-2"><Button variant="outline" onClick={() => navigate("/usecases")} className="h-10 rounded-none border-[var(--peer-line)] bg-white"><X className="size-4" />Cancel</Button><Button onClick={() => void saveDraft()} disabled={saveState === "saving"} className="h-10 rounded-none bg-[var(--peer-navy)] text-white"><Save className="size-4" />Save draft</Button></div>
      </header>

      {error ? <div className="mb-5 border-l-4 border-[var(--peer-danger)] bg-red-50 p-4 text-sm text-red-800">{error}</div> : null}

      <section className="peer-panel grid overflow-hidden lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="border-b border-[var(--peer-line)] bg-[#f5f4ef] p-5 lg:border-b-0 lg:border-r">
          <div className="grid gap-2">
            {[
              { n: 1, title: "Organization", detail: "Confirm your information", icon: Building2 },
              { n: 2, title: "Use case", detail: "Five practical questions", icon: BadgeCheck },
              { n: 3, title: "Location & files", detail: "Review and submit", icon: UploadCloud },
            ].map((item) => {
              const Icon = item.icon
              const active = step === item.n
              const complete = step > item.n
              return <button key={item.n} type="button" onClick={() => item.n < step && setStep(item.n)} className={`grid grid-cols-[38px_1fr] items-center gap-3 border p-3 text-left ${active ? "border-[var(--peer-teal)] bg-white" : "border-transparent"}`}><span className={`grid size-9 place-items-center border text-xs font-bold ${active || complete ? "border-[#bad5cf] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]" : "border-[var(--peer-line)] bg-white text-[var(--peer-muted)]"}`}>{complete ? <Check className="size-4" /> : <Icon className="size-4" />}</span><span><strong className="block text-sm">{item.title}</strong><small className="text-[11px] text-[var(--peer-muted)]">{item.detail}</small></span></button>
            })}
          </div>
        </aside>

        <div className="min-w-0 p-5 sm:p-7 lg:p-9">
          {step === 1 ? (
            <section>
              <p className="peer-eyebrow">Step 1 of 3</p><h2 className="mt-2 font-display text-2xl font-semibold">Confirm your organization information</h2><p className="mt-2 text-sm text-[var(--peer-muted)]">We filled in what PeerLink already knows. Correct only what has changed.</p>
              <div className="mt-5 flex items-start gap-3 border-l-4 border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] p-4 text-sm text-[var(--peer-navy)]"><BadgeCheck className="mt-0.5 size-5 shrink-0 text-[var(--peer-teal)]" /><span><strong className="block">Verified workspace information</strong>Organization and contributor details came from your profile so you do not have to enter them again.</span></div>
              <div className="mt-6 grid gap-5 md:grid-cols-2">
                <label className="text-xs font-bold">Organization *<Input value={form.organization} readOnly className="mt-2 h-11 rounded-none bg-[#f5f4ef]" /><FieldError>{errors.organization}</FieldError></label>
                <label className="text-xs font-bold">Factory or site name *<Input value={form.site} onChange={(e) => update("site", e.target.value)} placeholder="For example, Riyadh Innovation Center" className="mt-2 h-11 rounded-none" /><FieldError>{errors.site}</FieldError></label>
                <label className="text-xs font-bold">City *<select value={form.city} onChange={(e) => updateCity(e.target.value)} className="mt-2 h-11 w-full border border-input bg-white px-3 text-sm">{CITIES.map((city) => <option key={city}>{city}</option>)}</select><FieldError>{errors.city}</FieldError></label>
                <label className="text-xs font-bold">Submitted by *<span className="mt-2 flex h-11 items-center gap-2 border border-input bg-white px-3"><UserRound className="size-4 text-[var(--peer-teal)]" /><input value={form.submitter} onChange={(e) => update("submitter", e.target.value)} className="min-w-0 flex-1 bg-transparent text-sm outline-none" /></span><FieldError>{errors.submitter}</FieldError></label>
                <label className="text-xs font-bold">Job title<Input value={form.jobTitle} onChange={(e) => update("jobTitle", e.target.value)} className="mt-2 h-11 rounded-none" /></label>
                <label className="text-xs font-bold">Contact email *<Input type="email" value={form.email} onChange={(e) => update("email", e.target.value)} className="mt-2 h-11 rounded-none" /><FieldError>{errors.email}</FieldError></label>
              </div>
            </section>
          ) : null}

          {step === 2 ? (
            <section>
              <p className="peer-eyebrow">Step 2 of 3</p><h2 className="mt-2 font-display text-2xl font-semibold">Tell us about the use case</h2><p className="mt-2 text-sm text-[var(--peer-muted)]">Answer in your own words. Short, clear answers are enough.</p>
              <div className="mt-6 grid gap-4">
                <label className="text-xs font-bold">Use case title *<Input value={form.title} onChange={(e) => update("title", e.target.value)} placeholder="A short working title" maxLength={100} className="mt-2 h-11 rounded-none" /><FieldError>{errors.title}</FieldError></label>
                <label className="text-xs font-bold">Category<select value={form.category} onChange={(e) => update("category", e.target.value)} className="mt-2 h-11 w-full border border-input bg-white px-3 text-sm">{CATEGORIES.map((category) => <option key={category}>{category}</option>)}</select></label>
                <QuestionCard number="01" required label="What problem or opportunity was this use case intended to address?" help="Describe what was happening before the project and why the organization wanted to improve it." prompts={["What was happening before?", "Who or what was affected?", "Why did it need to improve?"]}><Textarea value={form.problem} onChange={(e) => update("problem", e.target.value)} placeholder="Write a short explanation in your own words…" className="min-h-28 rounded-none" maxLength={5000} /><FieldError>{errors.problem}</FieldError></QuestionCard>
                <QuestionCard number="02" required label="What technology, equipment, software, or approach was used?" help="List the main technologies in plain language. Detailed architecture is not required." prompts={["Equipment or hardware", "Software, platforms, or AI models", "How the parts worked together", "The implementation approach"]}><Textarea value={form.technology} onChange={(e) => update("technology", e.target.value)} placeholder="For example: camera, AI model, dashboard, sensors, integration approach…" className="min-h-28 rounded-none" maxLength={5000} /><FieldError>{errors.technology}</FieldError></QuestionCard>
                <QuestionCard number="03" label="What was the approximate project budget?" help="A range is enough. Choose ‘Prefer not to disclose’ when the information is confidential."><div className="grid gap-3 md:grid-cols-[1fr_.7fr]"><select value={form.budgetRange} onChange={(e) => update("budgetRange", e.target.value)} className="h-11 border border-input bg-white px-3 text-sm">{BUDGETS.map((budget) => <option key={budget}>{budget}</option>)}</select><Input value={form.budgetExact} onChange={(e) => update("budgetExact", e.target.value)} placeholder="Optional exact amount" className="h-11 rounded-none" /></div></QuestionCard>
                <QuestionCard number="04" required label="What changed after implementation?" help="Share improvements, savings, operational benefits, or lessons. Numbers are useful when available but are not mandatory." prompts={["What became faster, safer, cheaper, or more reliable?", "If measured: metric, before value, after value, and unit", "Any savings or operational benefits", "Qualitative improvements or lessons"]}><Textarea value={form.outcomes} onChange={(e) => update("outcomes", e.target.value)} placeholder="Only include measurements your organization actually observed…" className="min-h-32 rounded-none" maxLength={5000} /><FieldError>{errors.outcomes}</FieldError></QuestionCard>
                <QuestionCard number="05" label="What challenges did you experience?" help="Mention technical, operational, adoption, data, supplier, or implementation challenges if relevant." prompts={["What was difficult?", "How was it handled?", "What did the team learn?"]}><Textarea value={form.challenges} onChange={(e) => update("challenges", e.target.value)} placeholder="Optional" className="min-h-28 rounded-none" maxLength={1000} /><FieldError>{errors.challenges}</FieldError></QuestionCard>
              </div>
            </section>
          ) : null}

          {step === 3 ? (
            <section>
              <p className="peer-eyebrow">Step 3 of 3</p><h2 className="mt-2 font-display text-2xl font-semibold">Set the location, add files, and submit</h2><p className="mt-2 text-sm text-[var(--peer-muted)]">Confirm the exact site location, add optional supporting files, and review the submission.</p>
              <section className="mt-7">
                <div className="mb-4 flex items-start gap-3"><MapPin className="mt-0.5 size-5 shrink-0 text-[var(--peer-teal)]" /><div><h3 className="font-display text-lg font-semibold">Choose the factory location</h3><p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">This marker places the use case on the PeerLink map. Search for a location, click or drag the map marker, or enter coordinates directly.</p></div></div>
                <LocationPicker defaultLat={form.latitude} defaultLng={form.longitude} height="320px" onLocationSelect={(latitude, longitude) => setForm((current) => ({ ...current, latitude, longitude }))} />
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <label className="text-xs font-bold">Latitude *<Input type="number" step="any" value={form.latitude} onChange={(event) => update("latitude", Number(event.target.value))} className="mt-2 h-11 rounded-none" /><FieldError>{errors.latitude}</FieldError></label>
                  <label className="text-xs font-bold">Longitude *<Input type="number" step="any" value={form.longitude} onChange={(event) => update("longitude", Number(event.target.value))} className="mt-2 h-11 rounded-none" /><FieldError>{errors.longitude}</FieldError></label>
                </div>
              </section>
              <div className="mt-7 border-t border-[var(--peer-line)] pt-6"><h3 className="font-display text-lg font-semibold">Supporting files</h3><p className="mt-1 text-xs text-[var(--peer-muted)]">Attachments are optional. Add anything that helps reviewers understand the implementation.</p></div>
              <label className="mt-4 grid min-h-48 cursor-pointer place-items-center border border-dashed border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] p-6 text-center"><span><UploadCloud className="mx-auto size-9 text-[var(--peer-teal)]" /><strong className="mt-3 block font-display">Drop files here or browse your device</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">JPEG, PNG, WebP, MP4 or WebM<br />Up to 10 files · 5 MB images · 50 MB videos</span></span><input type="file" multiple accept="image/jpeg,image/png,image/webp,video/mp4,video/webm" className="sr-only" onChange={(e) => onFiles(e.target.files)} /></label>
              {files.length || existingImages.length ? <div className="mt-4 grid gap-2">{existingImages.map((url, index) => <div key={url} className="flex items-center gap-3 border border-[var(--peer-line)] p-3"><FileImage className="size-5 text-[var(--peer-teal)]" /><span className="min-w-0 flex-1 truncate text-sm">Existing attachment {index + 1}</span><button onClick={() => setExistingImages((current) => current.filter((_, i) => i !== index))} aria-label="Remove existing attachment"><X className="size-4" /></button></div>)}{files.map((file, index) => <div key={`${file.name}-${file.size}-${index}`} className="flex items-center gap-3 border border-[var(--peer-line)] p-3">{file.type.startsWith("video/") ? <FileVideo className="size-5 text-[var(--peer-teal)]" /> : <FileImage className="size-5 text-[var(--peer-teal)]" />}<span className="min-w-0 flex-1"><strong className="block truncate text-sm">{file.name}</strong><small className="text-[var(--peer-muted)]">{(file.size / 1024 / 1024).toFixed(1)} MB</small></span><button onClick={() => setFiles((current) => current.filter((_, i) => i !== index))} aria-label={`Remove ${file.name}`}><X className="size-4" /></button></div>)}</div> : null}
              <div className="mt-6 border border-[var(--peer-line)] bg-[#f5f4ef] p-5">
                <p className="peer-eyebrow">Submission summary</p><h3 className="mt-2 font-display text-lg font-semibold">Check the essentials before submitting</h3>
                <dl className="mt-4 text-sm">{[
                  ["Organization", `${form.organization}${form.site ? ` · ${form.site}` : ""}`], ["Use case", form.title || "Not entered"], ["Information provided", informationProvided || "Not entered"], ["Attachments", `${existingImages.length + files.length} file${existingImages.length + files.length === 1 ? "" : "s"}`], ["Next step", "PeerLink reviewers will check the submission before publication."],
                ].map(([label, value]) => <div key={label} className="grid gap-1 border-t border-[var(--peer-line)] py-3 sm:grid-cols-[150px_1fr]"><dt className="font-bold text-[var(--peer-muted)]">{label}</dt><dd>{value}</dd></div>)}</dl>
                <label className="mt-3 flex items-start gap-3 text-xs leading-5"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} className="mt-1 accent-[var(--peer-teal)]" /><span>I confirm that I am authorized to share this information and understand that it will be reviewed before publication.</span></label>
              </div>
            </section>
          ) : null}

          <footer className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-[var(--peer-line)] pt-5">
            {step === 1 ? <button onClick={() => navigate("/usecases")} className="inline-flex items-center gap-2 text-xs font-bold text-[var(--peer-blue)]"><ArrowLeft className="size-4" />Back to library</button> : <button onClick={() => setStep((current) => current - 1)} className="inline-flex items-center gap-2 text-xs font-bold text-[var(--peer-blue)]"><ArrowLeft className="size-4" />Previous step</button>}
            <div className="flex gap-2"><Button variant="outline" onClick={() => void saveDraft()} className="rounded-none border-[var(--peer-line)] bg-white"><Save className="size-4" />Save draft</Button>{step < 3 ? <Button onClick={() => void goNext()} className="rounded-none bg-[var(--peer-navy)] text-white">Continue<ArrowRight className="size-4" /></Button> : <Button onClick={() => void submit()} disabled={submitting} className="rounded-none bg-[var(--peer-teal)] text-white hover:bg-[#17636a]">{submitting ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}{editId ? "Update use case" : "Submit use case"}</Button>}</div>
          </footer>
        </div>
      </section>
      <p className="mt-4 flex items-center justify-center gap-2 text-xs text-[var(--peer-muted)]"><MapPin className="size-3.5" />The selected city provides a starting point; confirm the exact map location before submitting.</p>
    </main>
  )
}

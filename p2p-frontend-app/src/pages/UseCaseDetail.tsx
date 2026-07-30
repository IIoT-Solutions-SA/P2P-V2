import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react"
import { useParams } from "react-router-dom"
import {
  ArrowLeft,
  BadgeCheck,
  Bookmark,
  Building2,
  CalendarCheck,
  CircleAlert,
  Cpu,
  Download,
  Edit,
  Eye,
  Factory,
  FileText,
  Mail,
  MoreVertical,
  Route,
  Send,
  Share2,
  ShieldCheck,
  ThumbsUp,
  Trash2,
  TrendingUp,
  UserRound,
  Users,
  WalletCards,
  Wrench,
} from "lucide-react"
import { buildApiUrl } from "@/config/environment"
import { Button } from "@/components/ui/button"
import { DeleteConfirmModal } from "@/components/ui/DeleteConfirmModal"
import { MediaGallery } from "@/components/ui/MediaGallery"
import { ErrorState, LoadingState } from "@/components/shared/AppState"
import { useAuth } from "@/contexts/AuthContext"
import { useCasesApi } from "@/lib/api/usecases"
import { peopleApi, type OrganizationMember } from "@/lib/api/people"

interface DetailedUseCase {
  _id: string
  id?: string
  title: string
  title_slug?: string
  company_slug?: string
  company?: string
  organization_name?: string
  submitted_by?: string
  subtitle?: string
  last_updated?: string
  created_at?: string
  status?: string
  verified_by?: string
  category?: string
  factory_name?: string
  region?: string
  location?: { lat?: number; lng?: number }
  contact_person?: string
  contact_title?: string
  contact_email?: string
  images?: string[]
  videos?: Array<{ url: string; filename?: string; type?: string }>
  attachments?: Array<{ url: string; filename?: string; type?: string; size?: number }>
  executive_summary?: string
  problem?: string
  technology?: string
  budget?: string
  outcomes?: string
  challenges?: string
  business_challenge?: {
    industry_context?: string
    specific_problems?: string[]
    business_impact?: { financial_loss?: string; customer_impact?: string; operational_impact?: string; compliance_risk?: string }
  }
  solution_details?: {
    selection_criteria?: string[]
    vendor_evaluation?: { process?: string; selected_vendor?: string; selection_reasons?: string[] }
    technology_components?: Array<string | { component?: string; details?: string }>
  }
  implementation_details?: {
    methodology?: string
    total_budget?: string
    total_duration?: string
  }
  challenges_and_solutions?: Array<{ challenge?: string; description?: string; impact?: string; solution?: string; outcome?: string }>
  results?: {
    quantitative_metrics?: Array<{ metric?: string; baseline?: string; current?: string; improvement?: string }>
    qualitative_impacts?: string[]
    roi_analysis?: { total_investment?: string; annual_savings?: string; payback_period?: string; three_year_roi?: string }
  }
  view_count?: number
  views?: number
  likes?: number
  saves?: number
}

function AsideCard({ kicker, title, children }: { kicker: string; title: string; children: ReactNode }) {
  return <section className="peer-panel p-5"><p className="peer-eyebrow">{kicker}</p><h3 className="mt-1 font-display text-lg font-semibold">{title}</h3><div className="mt-4">{children}</div></section>
}

function StorySection({ label, title, icon: Icon, children }: { label: string; title: string; icon: typeof CircleAlert; children: ReactNode }) {
  return (
    <section className="relative border-t border-[var(--peer-line)] py-8 pl-0 first:border-t-0 first:pt-0 sm:pl-14">
      <span className="mb-4 grid size-10 place-items-center border border-[#c4d7d1] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)] sm:absolute sm:left-0 sm:top-8 sm:mb-0 sm:first:top-0"><Icon className="size-5" /></span>
      <p className="text-[10px] font-bold uppercase tracking-[.12em] text-[var(--peer-teal)]">{label}</p>
      <h2 className="mt-1 font-display text-2xl font-semibold tracking-[-.03em]">{title}</h2>
      <div className="mt-3 space-y-3 text-sm leading-7 text-[var(--peer-ink)]">{children}</div>
    </section>
  )
}

const clean = (value?: string) => value?.trim() || ""
const titleFromSlug = (slug?: string) => slug ? slug.replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase()).replace(/^Iiot\b/, "IIoT") : ""
const isPlaceholder = (value?: string) => /^(not specified|not provided|unknown|no challenges shared|no implementation challenges)/i.test(clean(value))
const firstSentence = (value: string, fallback: string) => clean(value).split(/[.!?\n]/)[0]?.trim() || fallback
const initials = (name: string) => name.split(/\s+/).map((part) => part[0]).join("").slice(0, 2).toUpperCase()
const isVideoUrl = (url: string) => /\.(mp4|webm)(?:\?|$)/i.test(url)

export default function UseCaseDetail() {
  const { company_slug, title_slug } = useParams<{ company_slug: string; title_slug: string }>()
  const { user } = useAuth()
  const [useCase, setUseCase] = useState<DetailedUseCase | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [ownerMenu, setOwnerMenu] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [bookmarked, setBookmarked] = useState(false)
  const [bookmarkCount, setBookmarkCount] = useState<number | null>(null)
  const [contactOpen, setContactOpen] = useState(false)
  const [contactProfile, setContactProfile] = useState<OrganizationMember | null>(null)
  const [contactLoading, setContactLoading] = useState(false)

  const fetchDetail = useCallback(async () => {
    if (!company_slug || !title_slug) { setError("Use case route is incomplete."); setLoading(false); return }
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(buildApiUrl(`/api/v1/use-cases/${company_slug}/${title_slug}`), { credentials: "include" })
      if (!response.ok) throw new Error("The use case could not be loaded.")
      const data = await response.json() as DetailedUseCase
      setUseCase(data)
      setBookmarkCount(data.saves ?? null)
      window.scrollTo(0, 0)
      void useCasesApi.bookmarks().then((saved) => setBookmarked(saved.some((item) => String(item.id) === String(data._id || data.id)))).catch(() => undefined)
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The use case could not be loaded.") }
    finally { setLoading(false) }
  }, [company_slug, title_slug])

  useEffect(() => { void fetchDetail() }, [fetchDetail])
  useEffect(() => {
    if (!ownerMenu) return
    const close = (event: MouseEvent) => { if (!(event.target as Element).closest("[data-owner-menu]")) setOwnerMenu(false) }
    document.addEventListener("click", close)
    return () => document.removeEventListener("click", close)
  }, [ownerMenu])

  const isAuthor = Boolean(user && useCase?.submitted_by && (user.id === useCase.submitted_by || (user as { mongo_id?: string }).mongo_id === useCase.submitted_by))

  const removeUseCase = async () => {
    if (!useCase) return
    try {
      const response = await fetch(buildApiUrl(`/api/v1/use-cases/${useCase._id}`), { method: "DELETE", credentials: "include" })
      if (!response.ok) throw new Error("The use case could not be deleted.")
      window.location.assign("/usecases")
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The use case could not be deleted."); setDeleteOpen(false) }
  }

  const toggleBookmark = async () => {
    if (!company_slug || !title_slug) return
    try {
      const result = await useCasesApi.bookmark(company_slug, title_slug)
      setBookmarked(result.bookmarked)
      setBookmarkCount(result.bookmarks)
    } catch { /* Authentication handling remains owned by the shared API client. */ }
  }

  const share = async () => {
    try {
      if (navigator.share) await navigator.share({ title: useCase?.title, url: window.location.href })
      else await navigator.clipboard.writeText(window.location.href)
    } catch { /* A cancelled native share needs no UI change. */ }
  }

  const openContact = async () => {
    setContactOpen(true)
    setContactProfile(null)
    if (!useCase?.contact_person) return
    setContactLoading(true)
    try {
      const result = await peopleApi.directory()
      const target = useCase.contact_person.trim().toLowerCase()
      setContactProfile(result.users.find((person) => {
        const fullName = (person.name || `${person.firstName || ""} ${person.lastName || ""}`).trim().toLowerCase()
        return fullName === target
      }) || null)
    } catch { setContactProfile(null) }
    finally { setContactLoading(false) }
  }

  const derived = useMemo(() => {
    if (!useCase) return null
    const specific = (useCase.business_challenge?.specific_problems || []).filter((item, index, all) => clean(item) && all.findIndex((candidate) => clean(candidate) === clean(item)) === index)
    const problem = clean(useCase.problem) || specific.join("\n\n") || clean(useCase.business_challenge?.industry_context) || clean(useCase.executive_summary)
    const components = (useCase.solution_details?.technology_components || []).map((item) => typeof item === "string" ? item : [item.component, item.details].filter(Boolean).join(": ")).filter((item) => clean(item) && !isPlaceholder(item))
    const technology = clean(useCase.technology) || components.join("\n\n") || (!isPlaceholder(useCase.implementation_details?.methodology) ? clean(useCase.implementation_details?.methodology) : "") || clean(useCase.subtitle)
    const qualitative = (useCase.results?.qualitative_impacts || []).filter((item) => clean(item))
    const meaningfulMetrics = (useCase.results?.quantitative_metrics || []).filter((item) => ![item.metric, item.baseline, item.current, item.improvement].some(isPlaceholder))
    const outcome = clean(useCase.outcomes) || qualitative.join("\n\n") || meaningfulMetrics.map((item) => [item.metric, item.improvement || item.current].filter(Boolean).join(": ")).join("\n") || clean(useCase.executive_summary)
    const challenges = (useCase.challenges_and_solutions || []).filter((item) => !isPlaceholder(item.challenge) && !isPlaceholder(item.description))
    const challengeText = clean(useCase.challenges) || challenges.map((item) => [item.challenge, item.description, item.solution && !isPlaceholder(item.solution) ? `Response: ${item.solution}` : "", item.outcome && !isPlaceholder(item.outcome) ? `Outcome: ${item.outcome}` : ""].filter(Boolean).join("\n")).join("\n\n")
    const budget = clean(useCase.budget) || (!isPlaceholder(useCase.implementation_details?.total_budget) ? clean(useCase.implementation_details?.total_budget) : "Not disclosed")
    const organization = clean(useCase.organization_name) || clean(useCase.company) || clean(useCase.factory_name) || titleFromSlug(useCase.company_slug || company_slug) || "PeerLink organization"
    const media = [
      ...(useCase.images || []).map((url, index) => ({ url, filename: `Project image ${index + 1}`, type: "image/jpeg", isVideo: isVideoUrl(url) })),
      ...(useCase.videos || []).map((item, index) => ({ url: item.url, filename: item.filename || `Project video ${index + 1}`, type: item.type || "video/mp4", isVideo: true })),
    ]
    const documents = (useCase.attachments || []).filter((item) => !item.type?.startsWith("image/") && !item.type?.startsWith("video/"))
    return { problem, technology, outcome, challengeText, budget, organization, media, documents, meaningfulMetrics }
  }, [company_slug, useCase])

  if (loading) return <div className="px-4 py-8 md:px-8 xl:px-14"><LoadingState title="Loading use case" description="Retrieving the contributor story and supporting evidence." /></div>
  if (error || !useCase || !derived) return <div className="px-4 py-8 md:px-8 xl:px-14"><ErrorState title="Use case unavailable" description={error || "The requested use case could not be found."} actionLabel="Back to use cases" onAction={() => window.location.assign("/usecases")} /></div>

  const views = useCase.views ?? useCase.view_count ?? 0
  const published = useCase.last_updated || useCase.created_at
  const storySections = [derived.problem, derived.technology, derived.outcome, derived.challengeText].filter(Boolean).length

  return (
    <main className="mx-auto w-full max-w-[1430px] px-4 py-7 md:px-8 md:py-10 xl:px-14">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <button type="button" onClick={() => window.location.assign("/usecases")} className="inline-flex min-h-10 items-center gap-2 text-xs font-bold text-[var(--peer-blue)]"><ArrowLeft className="size-4" />Back to use cases</button>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={() => void toggleBookmark()} className={`h-10 rounded-none border-[var(--peer-line)] bg-white text-xs ${bookmarked ? "text-[var(--peer-teal)]" : ""}`}><Bookmark className={`size-4 ${bookmarked ? "fill-current" : ""}`} />Save{bookmarkCount !== null ? ` ${bookmarkCount}` : ""}</Button>
          <Button variant="outline" onClick={() => void share()} className="h-10 rounded-none border-[var(--peer-line)] bg-white text-xs"><Share2 className="size-4" />Share</Button>
          <Button variant="outline" onClick={() => window.print()} className="hidden h-10 rounded-none border-[var(--peer-line)] bg-white text-xs sm:inline-flex"><Download className="size-4" />Download PDF</Button>
          {isAuthor ? <div className="relative" data-owner-menu><Button variant="outline" size="icon" onClick={() => setOwnerMenu((current) => !current)} className="size-10 rounded-none border-[var(--peer-line)] bg-white" aria-label="Manage use case"><MoreVertical className="size-4" /></Button>{ownerMenu ? <div className="absolute right-0 top-11 z-30 min-w-48 border border-[var(--peer-line)] bg-white shadow-[var(--peer-shadow)]"><button onClick={() => window.location.assign(`/submit?edit=${useCase._id}`)} className="flex w-full items-center gap-3 border-b border-[var(--peer-line)] px-4 py-3 text-left text-sm font-semibold hover:bg-[#f2f5f1]"><Edit className="size-4 text-[var(--peer-blue)]" />Edit use case</button><button onClick={() => { setDeleteOpen(true); setOwnerMenu(false) }} className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm font-semibold text-[var(--peer-danger)] hover:bg-red-50"><Trash2 className="size-4" />Delete use case</button></div> : null}</div> : null}
        </div>
      </div>

      <section className="peer-panel grid overflow-hidden lg:grid-cols-[minmax(0,1.45fr)_minmax(300px,.55fr)]">
        <div className="relative flex min-h-[365px] flex-col justify-between overflow-hidden bg-gradient-to-br from-[#083740] via-[#0a4d55] to-[#17636a] p-6 text-white sm:p-9">
          {useCase.images?.[0] ? <img src={useCase.images[0]} alt="" className="absolute inset-0 size-full object-cover opacity-25" /> : null}
          <div className="absolute inset-0 bg-gradient-to-t from-[rgba(7,40,47,.88)] via-[rgba(7,55,64,.45)] to-transparent" />
          <span className="relative z-10 inline-flex w-max items-center gap-2 text-xs font-bold text-[#d8ece8]"><BadgeCheck className="size-4" />{useCase.status === "verified" ? "PeerLink reviewed use case" : "Submitted use case"}</span>
          <div className="relative z-10">
            {useCase.category ? <span className="inline-flex min-h-8 items-center gap-2 border border-[rgba(118,197,189,.45)] bg-[rgba(118,197,189,.16)] px-3 text-xs font-bold text-[#d8ece8]"><Factory className="size-4" />{useCase.category}</span> : null}
            <h1 className="mt-4 max-w-4xl font-display text-3xl font-semibold leading-[1.12] tracking-[-.045em] sm:text-4xl xl:text-[50px]">{useCase.title}</h1>
            <p className="mt-4 text-sm text-[#c6d8d6]">{[derived.organization, useCase.factory_name, useCase.region].filter((item, index, all) => item && all.indexOf(item) === index).join(" · ")}</p>
          </div>
        </div>
        <aside className="flex flex-col justify-between gap-6 bg-white p-7">
          <div><p className="peer-eyebrow">At a glance</p><h2 className="mt-2 font-display text-2xl font-semibold">A practical manufacturing story</h2><p className="mt-2 text-xs leading-5 text-[var(--peer-muted)]">This page organizes the contributor’s answers without inventing technical detail or mandatory ROI figures.</p></div>
          <ul className="grid text-sm">
            <li className="grid grid-cols-[30px_1fr] gap-2 border-t border-[var(--peer-line)] py-3"><Cpu className="mt-0.5 size-4 text-[var(--peer-teal)]" /><span><small className="block uppercase tracking-wider text-[var(--peer-muted)]">Technology</small><strong>{firstSentence(derived.technology, "Approach described by contributor")}</strong></span></li>
            <li className="grid grid-cols-[30px_1fr] gap-2 border-t border-[var(--peer-line)] py-3"><WalletCards className="mt-0.5 size-4 text-[var(--peer-teal)]" /><span><small className="block uppercase tracking-wider text-[var(--peer-muted)]">Budget</small><strong>{derived.budget}</strong></span></li>
            <li className="grid grid-cols-[30px_1fr] gap-2 border-t border-[var(--peer-line)] py-3"><Building2 className="mt-0.5 size-4 text-[var(--peer-teal)]" /><span><small className="block uppercase tracking-wider text-[var(--peer-muted)]">Organization</small><strong>{derived.organization}</strong></span></li>
            {published ? <li className="grid grid-cols-[30px_1fr] gap-2 border-y border-[var(--peer-line)] py-3"><CalendarCheck className="mt-0.5 size-4 text-[var(--peer-teal)]" /><span><small className="block uppercase tracking-wider text-[var(--peer-muted)]">Published</small><strong>{new Date(published).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })}</strong></span></li> : null}
          </ul>
          {useCase.contact_person ? <Button onClick={() => void openContact()} className="h-11 rounded-none bg-[var(--peer-navy)] text-white hover:bg-[#174550]"><Send className="size-4" />Contact contributor</Button> : null}
        </aside>
      </section>

      <div className="mt-6 grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
        <article className="peer-panel p-6 sm:p-8">
          {derived.problem ? <StorySection label="Problem to solve" title="The problem or opportunity" icon={CircleAlert}>{derived.problem.split(/\n{2,}/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}</StorySection> : null}
          {derived.technology ? <StorySection label="Technology used" title="Technology and approach" icon={Cpu}>{derived.technology.split(/\n{2,}/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}</StorySection> : null}
          {derived.outcome ? <StorySection label="Outcomes and results" title="Observed outcomes" icon={TrendingUp}>{derived.outcome.split(/\n{2,}/).map((paragraph, index) => <p key={index}>{paragraph}</p>)}<p className="border-l-2 border-[var(--peer-teal)] pl-3 text-xs text-[var(--peer-muted)]"><strong>Contributor note:</strong> Results are presented as shared. PeerLink does not add percentages or ROI calculations that were not supplied.</p></StorySection> : null}
          {derived.challengeText ? <StorySection label="Challenges" title="Implementation challenges" icon={Route}>{derived.challengeText.split(/\n{2,}/).map((paragraph, index) => <p key={index} className="whitespace-pre-line">{paragraph}</p>)}</StorySection> : null}

          {derived.media.length || derived.documents.length ? <section className="border-t border-[var(--peer-line)] pt-8"><p className="peer-eyebrow">Supporting evidence</p><h2 className="mt-1 font-display text-2xl font-semibold">Images, videos and project files</h2><p className="mt-2 text-sm text-[var(--peer-muted)]">Supporting material supplied with the use case.</p>{derived.media.length ? <div className="mt-5"><MediaGallery items={derived.media} /></div> : null}{derived.documents.length ? <div className="mt-5 grid gap-2">{derived.documents.map((item, index) => <a key={`${item.url}-${index}`} href={item.url} target="_blank" rel="noreferrer" className="grid grid-cols-[38px_1fr_auto] items-center gap-3 border border-[var(--peer-line)] p-3"><span className="grid size-9 place-items-center bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><FileText className="size-4" /></span><span><strong className="block text-sm">{item.filename || `Project document ${index + 1}`}</strong><small className="text-[var(--peer-muted)]">{item.type || "Document"}</small></span><Download className="size-4" /></a>)}</div> : null}</section> : null}

          {!storySections ? <div className="py-10 text-center"><Wrench className="mx-auto size-8 text-[var(--peer-teal)]" /><h2 className="mt-3 font-display text-xl font-semibold">Publication review in progress</h2><p className="mt-2 text-sm text-[var(--peer-muted)]">The contributor’s story has not yet been organized into the simplified public format.</p></div> : null}
        </article>

        <aside className="grid gap-4 xl:sticky xl:top-[calc(var(--peer-topbar-height)+22px)]">
          <AsideCard kicker="Project information" title="Submitted details"><dl className="text-xs">{[
            ["Organization", derived.organization], ["Site", useCase.factory_name || "Not provided"], ["Location", useCase.region || "Not provided"], ["Budget", derived.budget], ["Attachments", String(derived.media.length + derived.documents.length)],
          ].map(([label, value]) => <div key={label} className="flex justify-between gap-3 border-t border-[var(--peer-line)] py-3 first:border-t-0 first:pt-0"><dt className="text-[var(--peer-muted)]">{label}</dt><dd className="text-right font-bold">{value}</dd></div>)}</dl></AsideCard>

          {useCase.contact_person ? <AsideCard kicker="Submitted by" title={useCase.contact_person}><div className="flex items-center gap-3"><span className="grid size-12 place-items-center rounded-full bg-[var(--peer-teal-soft)] font-display font-bold text-[var(--peer-teal)]">{initials(useCase.contact_person)}</span><p className="text-xs text-[var(--peer-muted)]">{useCase.contact_title || "Contributor"}<br />{derived.organization}</p></div><Button variant="outline" onClick={() => void openContact()} className="mt-4 h-10 w-full rounded-none border-[var(--peer-line)] bg-white"><UserRound className="size-4" />View profile</Button></AsideCard> : null}

          <AsideCard kicker="Publication review" title={useCase.status === "verified" ? "Reviewed by PeerLink" : "Submitted for review"}><p className="text-xs leading-5 text-[var(--peer-muted)]">PeerLink organizes the contributor’s information for clear publication without requiring a technical report.</p><div className="mt-4 flex gap-2 border-l-3 border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] p-3 text-xs leading-5 text-[var(--peer-navy)]"><ShieldCheck className="size-4 shrink-0 text-[var(--peer-teal)]" /><span>The wording is presented without inventing results or implementation claims.</span></div></AsideCard>

          <AsideCard kicker="Community" title="Peer engagement"><dl className="grid gap-3 text-xs"><div className="flex items-center justify-between"><span className="flex items-center gap-2"><Eye className="size-4 text-[var(--peer-teal)]" />Views</span><strong>{views.toLocaleString()}</strong></div>{useCase.likes !== undefined ? <div className="flex items-center justify-between"><span className="flex items-center gap-2"><ThumbsUp className="size-4 text-[var(--peer-teal)]" />Likes</span><strong>{useCase.likes}</strong></div> : null}</dl></AsideCard>
        </aside>
      </div>

      {contactOpen ? <div className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(7,25,31,.62)] p-4" role="dialog" aria-modal="true" onClick={() => setContactOpen(false)}><section className="w-full max-w-lg border border-[var(--peer-line)] bg-white shadow-[var(--peer-shadow)]" onClick={(event) => event.stopPropagation()}><header className="flex items-start justify-between border-b border-[var(--peer-line)] p-5"><div><p className="peer-eyebrow">Implementation contact</p><h2 className="mt-1 font-display text-2xl font-semibold">{useCase.contact_person}</h2><p className="mt-1 text-sm text-[var(--peer-muted)]">{useCase.contact_title || "Contributor"}</p></div><button onClick={() => setContactOpen(false)} className="grid size-10 place-items-center border border-[var(--peer-line)]" aria-label="Close contact profile">×</button></header><div className="p-5">{contactLoading ? <p className="py-8 text-center text-sm text-[var(--peer-muted)]">Loading network profile…</p> : <div className="grid gap-5"><div className="flex items-center gap-4"><span className="grid size-14 place-items-center rounded-full bg-[var(--peer-teal-soft)] font-display text-lg font-bold text-[var(--peer-teal)]">{initials(useCase.contact_person || "Contact")}</span><span><strong className="block">{contactProfile?.name || `${contactProfile?.firstName || ""} ${contactProfile?.lastName || ""}`.trim() || useCase.contact_person}</strong><span className="text-sm text-[var(--peer-muted)]">{contactProfile?.title || useCase.contact_title || "Contributor"}</span></span></div><dl className="grid gap-3 border-y border-[var(--peer-line)] py-4 text-sm"><div><dt className="peer-eyebrow">Organization</dt><dd className="mt-1 font-semibold">{contactProfile?.company || derived.organization}</dd></div><div><dt className="peer-eyebrow">Location</dt><dd className="mt-1 font-semibold">{contactProfile?.location || useCase.region || "Saudi Arabia"}</dd></div></dl><div className="flex flex-wrap gap-2">{contactProfile?.email || useCase.contact_email ? <Button asChild className="rounded-none bg-[var(--peer-navy)] text-white"><a href={`mailto:${contactProfile?.email || useCase.contact_email}`}><Mail className="size-4" />Email contributor</a></Button> : <Button disabled className="rounded-none">Email unavailable</Button>}<Button variant="outline" onClick={() => window.location.assign("/connect")} className="rounded-none border-[var(--peer-line)] bg-white"><Users className="size-4" />Browse network</Button></div></div>}</div></section></div> : null}

      <DeleteConfirmModal isOpen={deleteOpen} onClose={() => setDeleteOpen(false)} onConfirm={removeUseCase} title="Delete Use Case?" message="Are you sure you want to delete this use case? This action cannot be undone." itemName={useCase.title} />
    </main>
  )
}

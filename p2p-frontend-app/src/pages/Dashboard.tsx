import { useCallback, useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import {
  ArrowRight,
  ArrowUpRight,
  Eye,
  Factory,
  MessageCircleQuestion,
  Network,
  NotebookPen,
  UserSearch,
  UsersRound,
} from "lucide-react"
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/AppState"
import { dashboardApi, type DashboardStats, type ForumDraft } from "@/lib/api/dashboard"
import { useCasesApi, type UseCaseDraftListItem, type UseCaseListItem } from "@/lib/api/usecases"
import { peopleApi, type OrganizationMember } from "@/lib/api/people"
import { useAuth } from "@/contexts/AuthContext"
import { cn } from "@/lib/utils"
import { formatOrganizationName } from "@/lib/formatters"

const defaultStats: DashboardStats = {
  questions_asked: 0,
  answers_given: 0,
  bookmarks_saved: 0,
  reputation_score: 0,
  activity_level: 0,
  use_cases_submitted: 0,
  best_answers: 0,
  draft_posts: 0,
  connections_count: 0,
}

const memberName = (member: OrganizationMember) =>
  member.name || `${member.firstName || ""} ${member.lastName || ""}`.trim() || member.email

const initials = (value: string) =>
  value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "PL"

const impactFacts = (item?: UseCaseListItem) => {
  if (!item) return []
  const benefits = item.results?.benefits
  if (typeof benefits === "string") {
    return benefits.split(";").map((value) => value.trim()).filter(Boolean).slice(0, 3)
  }
  return []
}

export default function Dashboard() {
  const { user, organization } = useAuth()
  const [stats, setStats] = useState<DashboardStats>(defaultStats)
  const [forumDrafts, setForumDrafts] = useState<ForumDraft[]>([])
  const [useCaseDrafts, setUseCaseDrafts] = useState<UseCaseDraftListItem[]>([])
  const [featuredCases, setFeaturedCases] = useState<UseCaseListItem[]>([])
  const [members, setMembers] = useState<OrganizationMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [statsData, forumDraftData, useCaseDraftData, caseData, peopleData] = await Promise.all([
        dashboardApi.stats().catch(() => defaultStats),
        dashboardApi.forumDrafts().catch(() => ({ drafts: [], total: 0 })),
        useCasesApi.drafts().catch(() => []),
        useCasesApi.list({ limit: 4, sortBy: "newest" }).catch(() => ({ items: [], total: 0, limit: 4, skip: 0, has_more: false })),
        peopleApi.organizationMembers().catch(() => ({ users: [] })),
      ])
      setStats(statsData)
      setForumDrafts(forumDraftData.drafts || [])
      setUseCaseDrafts(useCaseDraftData || [])
      setFeaturedCases(caseData.items || [])
      setMembers(peopleData.users || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadDashboard()
  }, [loadDashboard])

  const name = useMemo(
    () => `${user?.firstName || ""} ${user?.lastName || ""}`.trim() || user?.email || "PeerLink member",
    [user],
  )
  const firstName = user?.firstName || name.split(" ")[0]
  const organizationName = formatOrganizationName(organization?.name || user?.company, "Your organization")
  const allDrafts = useMemo(
    () => [
      ...useCaseDrafts.map((draft) => ({ href: `/submit?draft=${draft.id}`, label: "Use-case draft", detail: draft.title || "Untitled use case" })),
      ...forumDrafts.map((draft) => ({ href: "/forum", label: "Forum draft", detail: draft.title || "Untitled discussion" })),
    ],
    [forumDrafts, useCaseDrafts],
  )
  const featured = featuredCases[0]
  const facts = impactFacts(featured)
  const connectedMembers = members.filter((member) => member.isActive !== false).slice(0, 4)
  const today = new Intl.DateTimeFormat("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    timeZone: "Asia/Riyadh",
  }).format(new Date())

  if (loading) return <div className="px-5 py-10 md:px-8 xl:px-[58px]"><LoadingState title="Loading network workspace" /></div>
  if (error) return <div className="px-5 py-10 md:px-8 xl:px-[58px]"><ErrorState title="Dashboard unavailable" description={error} actionLabel="Retry" onAction={() => void loadDashboard()} /></div>

  return (
    <div className="min-h-[calc(100vh-var(--peer-topbar-height))] bg-[var(--peer-paper)] [--peer-surface:#ffffff]">
      <div className="mx-auto w-full max-w-[1430px] px-5 pb-16 pt-8 md:px-8 md:pt-11 xl:px-[58px]">
        <header className="mb-8 grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_auto] md:gap-7">
        <div>
          <p className="peer-eyebrow mb-1.5">{today}</p>
          <h1 className="font-display max-w-[760px] text-[clamp(30px,3.3vw,45px)] font-semibold leading-[1.13] tracking-[-0.045em] text-[var(--peer-ink)]">
            Good morning, {firstName}. What can the network move forward today?
          </h1>
          <p className="mt-2 text-[15px] text-[var(--peer-muted)]">Your working view of shared knowledge, collaborators and contributions.</p>
        </div>
        <div className="min-w-[215px] border-l-2 border-[var(--peer-teal)] py-1 pl-4">
          <strong className="font-display block text-sm font-semibold">{organizationName}</strong>
          <span className="text-xs text-[var(--peer-muted)]">{user?.title || "Manufacturing professional"} · {user?.role === "admin" ? "Admin" : "Member"}</span>
        </div>
      </header>

      <div className="grid items-start gap-[22px] lg:grid-cols-[minmax(0,1.7fr)_minmax(290px,0.78fr)]">
        <div className="flex min-w-0 flex-col gap-[22px]">
        <section className="peer-panel lg:col-start-1" aria-labelledby="start-something-title">
          <div className="border-b border-[var(--peer-line)] px-[23px] py-[18px]">
            <p className="peer-eyebrow mb-1">Create or connect</p>
            <h2 id="start-something-title" className="font-display text-[19px] font-semibold tracking-[-0.025em]">Start something useful</h2>
          </div>
          <div className="grid sm:grid-cols-2">
            {[
              { href: "/forum?compose=true", title: "Ask a question", copy: "Bring a manufacturing challenge to the community.", icon: MessageCircleQuestion },
              { href: "/submit", title: "Share a use case", copy: "Document an implementation your peers can reuse.", icon: NotebookPen },
              { href: "/connect", title: "Find collaborators", copy: "Connect with specialists across the network.", icon: UserSearch },
              { href: "/organization", title: organizationName, copy: "View your organization profile and members.", icon: UsersRound },
            ].map(({ href, title, copy, icon: Icon }, index) => (
              <Link
                key={title}
                to={href}
                className={cn(
                  "group grid min-h-[116px] grid-cols-[39px_1fr_20px] items-start gap-3 border-[var(--peer-line)] p-[22px] transition hover:bg-[#f2f5f1]",
                  index % 2 === 0 && "sm:border-r",
                  index < 2 && "border-b",
                  index === 2 && "border-b sm:border-b-0",
                )}
              >
                <span className="grid size-[39px] place-items-center border border-[#c4d7d1] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><Icon className="size-[19px]" strokeWidth={1.8} /></span>
                <span><strong className="mb-1 block text-sm">{title}</strong><span className="block text-xs leading-[1.4] text-[var(--peer-muted)]">{copy}</span></span>
                <ArrowUpRight className="mt-2 size-[17px] text-[#899295] transition group-hover:text-[var(--peer-teal)]" />
              </Link>
            ))}
          </div>
        </section>

        {featuredCases.length > 1 ? (
          <section className="peer-panel" aria-labelledby="keep-exploring-title">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--peer-line)] px-[23px] py-[16px]">
              <div>
                <p className="peer-eyebrow mb-1">From the network</p>
                <h2 id="keep-exploring-title" className="font-display text-[18px] font-semibold tracking-[-0.025em]">Keep exploring</h2>
              </div>
              <Link to="/usecases" className="inline-flex items-center gap-1 text-xs font-bold text-[var(--peer-blue)]">Browse all <ArrowRight className="size-3.5" /></Link>
            </div>
            <div className="grid sm:grid-cols-2">
              {featuredCases.slice(1, 3).map((item, index) => (
                <Link
                  key={item.id}
                  to={`/usecases/${item.company_slug}/${item.title_slug}`}
                  className={cn("group grid min-w-0 grid-cols-[1fr_auto] gap-3 px-[22px] py-[17px] hover:bg-[#f2f5f1]", index === 0 && "sm:border-r sm:border-[var(--peer-line)]")}
                >
                  <span className="min-w-0">
                    <strong className="block truncate text-[13px]">{item.title}</strong>
                    <span className="mt-1 block truncate text-[11px] text-[var(--peer-muted)]">{item.category} · {item.company}</span>
                  </span>
                  <ArrowUpRight className="mt-1 size-4 text-[#899295] transition group-hover:text-[var(--peer-teal)]" />
                </Link>
              ))}
            </div>
          </section>
        ) : null}


        <section className="peer-panel overflow-hidden lg:grid lg:grid-cols-[minmax(0,1.5fr)_minmax(245px,0.5fr)]" aria-labelledby="featured-title">
          <div className="relative min-h-[254px] overflow-hidden bg-[var(--peer-navy)] px-6 py-8 text-white md:px-9">
            <div className="absolute -bottom-28 -right-9 h-[270px] w-[310px] -rotate-[18deg] border border-[#75c3ba40]" />
            <p className="peer-eyebrow relative z-10 !text-[#76c5bd]">Featured implementation</p>
            <h2 id="featured-title" className="font-display relative z-10 my-4 max-w-[680px] text-[clamp(23px,2.6vw,33px)] font-semibold leading-[1.22] tracking-[-0.035em]">{featured?.title || "Manufacturing knowledge moves further when teams share what worked"}</h2>
            <p className="relative z-10 mb-6 max-w-[650px] text-[13px] text-[#b8cdca]">{featured?.description || "Explore a field-tested implementation from the PeerLink network, including practical methods, measured outcomes and lessons for reuse."}</p>
            {featured ? <Link to={`/usecases/${featured.company_slug}/${featured.title_slug}`} className="relative z-10 inline-flex min-h-10 items-center gap-2 bg-white px-4 text-xs font-bold text-[var(--peer-navy)] hover:bg-[#e6efed]">Read implementation <ArrowUpRight className="size-4" /></Link> : <Link to="/usecases" className="relative z-10 inline-flex min-h-10 items-center gap-2 bg-white px-4 text-xs font-bold text-[var(--peer-navy)]">Explore use cases <ArrowUpRight className="size-4" /></Link>}
          </div>
          <div className="grid content-center bg-[#e1e7e2] p-7">
            <dl>
              <div className="grid grid-cols-[1fr_auto] gap-3 border-b border-[#c4ccc6] py-3.5"><dt className="text-[11px] text-[var(--peer-muted)]">Organization</dt><dd className="font-display text-right text-[13px] font-bold">{featured?.company || "PeerLink network"}</dd></div>
              <div className="grid grid-cols-[1fr_auto] gap-3 border-b border-[#c4ccc6] py-3.5"><dt className="text-[11px] text-[var(--peer-muted)]">Category</dt><dd className="font-display text-right text-[13px] font-bold">{featured?.category || "Manufacturing"}</dd></div>
              <div className="grid grid-cols-[1fr_auto] gap-3 py-3.5"><dt className="text-[11px] text-[var(--peer-muted)]">Measured impact</dt><dd className="font-display max-w-[150px] text-right text-sm font-bold text-[var(--peer-teal)]">{facts[0] || featured?.timeframe || "Field-tested"}</dd></div>
            </dl>
            <div className="mt-2 flex items-center gap-2 text-[11px] text-[var(--peer-muted)]"><Eye className="size-3.5" />{featured?.views || 0} network views <Factory className="ml-2 size-3.5" />Verified story</div>
          </div>
        </section>
        </div>
        <div className="flex min-w-0 flex-col gap-[22px]">
        <aside className="peer-panel lg:col-start-2 lg:row-start-1" aria-labelledby="workspace-pulse-title">
          <div className="border-b border-[var(--peer-line)] px-[23px] py-[18px]">
            <p className="peer-eyebrow mb-1">Your contribution</p>
            <h2 id="workspace-pulse-title" className="font-display text-[19px] font-semibold tracking-[-0.025em]">Workspace pulse</h2>
          </div>
          <div className="border-b border-[var(--peer-line)] px-[23px] py-6">
            <div className="mb-2 flex items-baseline gap-2"><strong className="font-display text-[38px] font-semibold leading-none tracking-[-0.05em]">{stats.activity_level}%</strong><span className="text-xs text-[var(--peer-muted)]">activity level</span></div>
            <p className="mb-4 text-xs text-[var(--peer-muted)]">One useful contribution this week will move your profile forward.</p>
            <div className="h-[5px] overflow-hidden bg-[#deded7]" role="progressbar" aria-label="Activity level" aria-valuemin={0} aria-valuemax={100} aria-valuenow={stats.activity_level}>
              <div className="h-full bg-[var(--peer-teal)]" style={{ width: `${Math.min(100, Math.max(0, stats.activity_level))}%` }} />
            </div>
          </div>
          <dl>
            {[
              ["Questions", stats.questions_asked],
              ["Answers", stats.answers_given],
              ["Saved", stats.bookmarks_saved],
              ["Use cases", stats.use_cases_submitted],
              ["Reputation", stats.reputation_score],
            ].map(([label, value], index) => (
              <div key={label} className="flex items-center justify-between border-b border-[var(--peer-line)] px-[22px] py-[15px] last:border-b-0">
                <dt className="text-xs text-[var(--peer-muted)]">{label}</dt>
                <dd className={cn("font-display text-[17px] font-semibold", index > 2 && "text-[var(--peer-teal)]")}>{value}</dd>
              </div>
            ))}
          </dl>
          <div className="mx-[22px] border-t border-[var(--peer-line)] py-4">
            {allDrafts[0] ? (
              <Link to={allDrafts[0].href} className="grid grid-cols-[1fr_auto] items-center gap-3">
                <span><strong className="mb-0.5 block text-[13px]">Continue where you left off</strong><span className="block text-[11px] text-[var(--peer-muted)]">{allDrafts[0].label} · {allDrafts[0].detail}</span></span>
                <span className="font-display text-[22px] font-bold text-[var(--peer-amber)]">{allDrafts.length}</span>
              </Link>
            ) : (
              <Link to="/submit" className="grid grid-cols-[1fr_auto] items-center gap-3">
                <span><strong className="mb-0.5 block text-[13px]">No open drafts</strong><span className="block text-[11px] text-[var(--peer-muted)]">Start documenting a reusable implementation.</span></span>
                <ArrowRight className="size-4 text-[var(--peer-teal)]" />
              </Link>
            )}
          </div>
        </aside>

        <section className="peer-panel lg:col-start-2" aria-labelledby="network-title">
          <div className="flex items-start justify-between gap-4 border-b border-[var(--peer-line)] px-5 py-[18px]">
            <div><p className="peer-eyebrow mb-1">Available now</p><h2 id="network-title" className="font-display text-[19px] font-semibold tracking-[-0.025em]">Your network</h2></div>
            <Link to="/connect" className="inline-flex items-center gap-1 text-xs font-bold text-[var(--peer-blue)]">People <ArrowRight className="size-3.5" /></Link>
          </div>
          <div>
            {connectedMembers.map((member, index) => {
              const person = memberName(member)
              return (
                <Link key={member.id} to="/connect" className="grid grid-cols-[39px_minmax(0,1fr)_7px] items-center gap-3 border-b border-[var(--peer-line)] px-5 py-3.5 last:border-b-0 hover:bg-[#f2f5f1]">
                  <span className="grid size-[39px] place-items-center overflow-hidden rounded-full bg-[#dfe8e5] text-xs font-bold text-[var(--peer-teal)]">{member.profilePictureUrl ? <img src={member.profilePictureUrl} alt="" className="size-full object-cover" /> : initials(person)}</span>
                  <span className="min-w-0"><strong className="block truncate text-xs">{person}</strong><span className="block truncate text-[10px] text-[var(--peer-muted)]">{member.title || member.expertiseTags?.[0] || "Manufacturing network member"}</span></span>
                  <span className={cn("size-[7px] rounded-full", index === 3 ? "bg-[#ca832f]" : "bg-[#1b8f75]")} />
                </Link>
              )
            })}
            {connectedMembers.length === 0 ? <EmptyState className="m-4 min-h-40 shadow-none" title="Your network is quiet" description="Organization members will appear here." /> : null}
          </div>
          <div className="flex items-center gap-2 border-t border-[var(--peer-line)] bg-[#f1f2ed] px-5 py-3.5 text-[11px] text-[var(--peer-muted)]"><Network className="size-4 text-[var(--peer-teal)]" />{members.length} verified colleagues in {organizationName}</div>
        </section>

        </div>
      </div>

      </div>
    </div>
  )
}

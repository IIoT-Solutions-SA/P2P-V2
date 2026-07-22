import { useCallback, useEffect, useMemo, useState } from "react"
import type { FormEvent, ReactNode } from "react"
import { Link } from "react-router-dom"
import {
  ArrowRight,
  Ban,
  Building2,
  CalendarDays,
  Check,
  CheckCircle2,
  Clock3,
  Factory,
  Globe2,
  Mail,
  MoreHorizontal,
  Search,
  Shield,
  ShieldCheck,
  UserCog,
  UserPlus,
  X,
} from "lucide-react"
import { Avatar } from "@/components/ui/Avatar"
import { Button } from "@/components/ui/button"
import { AccessDeniedState, EmptyState, ErrorState, LoadingState } from "@/components/shared/AppState"
import { useAuth } from "@/contexts/AuthContext"
import { peopleApi, type OrganizationMember } from "@/lib/api/people"
import { organizationApi, type Invitation } from "@/lib/api/organization"
import { useCasesApi, type UseCaseListItem } from "@/lib/api/usecases"
import { formatOrganizationName } from "@/lib/formatters"

type Tab = "roster" | "invitations" | "permissions" | "settings"
type RoleFilter = "all" | "admin" | "member"
type StatusFilter = "all" | "active" | "inactive"

const memberName = (member: OrganizationMember) =>
  member.name || `${member.firstName || ""} ${member.lastName || ""}`.trim() || member.email

const formatDate = (value?: string | Date | null) => {
  if (!value) return "Not available"
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? "Not available" : date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" })
}

const normalized = (value?: string | null) => (value || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "")

function DetailRow({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div className="border-b border-[var(--peer-line)] px-5 py-4 last:border-b-0">
      <dt className="text-[10px] font-bold uppercase tracking-[0.13em] text-[var(--peer-muted)]">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-[var(--peer-ink)]">{value || "Not available"}</dd>
    </div>
  )
}

function Metric({ label, value, note }: { label: string; value: ReactNode; note?: string }) {
  return (
    <div className="min-w-0 border-b border-r border-[var(--peer-line)] p-4 last:border-r-0 sm:p-5">
      <p className="text-[11px] text-[var(--peer-muted)]">{label}</p>
      <div className="mt-1 flex items-baseline gap-2">
        <strong className="font-display text-2xl font-semibold tracking-[-0.04em]">{value}</strong>
        {note ? <span className="text-[10px] font-semibold text-[var(--peer-teal)]">{note}</span> : null}
      </div>
    </div>
  )
}

function Capability({ title, description, member, administrator }: { title: string; description: string; member: boolean; administrator: boolean }) {
  const state = (allowed: boolean) => (
    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${allowed ? "text-[var(--peer-teal)]" : "text-[var(--peer-muted)]"}`}>
      {allowed ? <Check className="size-3.5" /> : <X className="size-3.5" />}
      {allowed ? "Allowed" : "Not allowed"}
    </span>
  )

  return (
    <div className="grid gap-3 border-b border-[var(--peer-line)] px-5 py-4 last:border-b-0 md:grid-cols-[minmax(0,1fr)_140px_140px] md:items-center">
      <div>
        <p className="text-sm font-semibold">{title}</p>
        <p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">{description}</p>
      </div>
      <div><span className="mr-2 text-[10px] font-bold uppercase text-[var(--peer-muted)] md:hidden">Member</span>{state(member)}</div>
      <div><span className="mr-2 text-[10px] font-bold uppercase text-[var(--peer-muted)] md:hidden">Administrator</span>{state(administrator)}</div>
    </div>
  )
}

export default function Organization() {
  const { user, organization } = useAuth()
  const [members, setMembers] = useState<OrganizationMember[]>([])
  const [invitations, setInvitations] = useState<Invitation[]>([])
  const [organizationUseCases, setOrganizationUseCases] = useState<UseCaseListItem[]>([])
  const [useCasesAvailable, setUseCasesAvailable] = useState(true)
  const [tab, setTab] = useState<Tab>("roster")
  const [query, setQuery] = useState("")
  const [roleFilter, setRoleFilter] = useState<RoleFilter>("all")
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all")
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [inviteEmail, setInviteEmail] = useState("")
  const [notice, setNotice] = useState<{ kind: "success" | "error"; message: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [cancellingId, setCancellingId] = useState<string | null>(null)
  const isAdmin = user?.role === "admin"
  const organizationName = formatOrganizationName(organization?.name || user?.company)

  const loadOrganization = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [peopleData, invitationData, useCaseData] = await Promise.all([
        peopleApi.organizationMembers(),
        isAdmin ? organizationApi.invitations().catch(() => ({ invitations: [], total: 0 })) : Promise.resolve({ invitations: [], total: 0 }),
        useCasesApi.list({ search: organizationName, sortBy: "newest", limit: 20, skip: 0 }).catch(() => null),
      ])
      const nextMembers = peopleData.users || []
      setMembers(nextMembers)
      setSelectedId((current) => current && nextMembers.some((member) => member.id === current) ? current : nextMembers[0]?.id || null)
      setInvitations(invitationData.invitations || [])
      if (useCaseData) {
        const organizationKey = normalized(organizationName)
        setOrganizationUseCases((useCaseData.items || []).filter((item) => normalized(item.company) === organizationKey).slice(0, 3))
        setUseCasesAvailable(true)
      } else {
        setOrganizationUseCases([])
        setUseCasesAvailable(false)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load organization")
    } finally {
      setLoading(false)
    }
  }, [isAdmin, organizationName])

  useEffect(() => {
    void loadOrganization()
  }, [loadOrganization])

  useEffect(() => {
    if (!isAdmin && tab !== "roster") setTab("roster")
  }, [isAdmin, tab])

  const filteredMembers = useMemo(() => {
    const needle = query.toLowerCase().trim()
    return members.filter((member) => {
      const matchesQuery = !needle || [memberName(member), member.email, member.role, member.title, member.location, ...(member.expertiseTags || [])].join(" ").toLowerCase().includes(needle)
      const matchesRole = roleFilter === "all" || member.role === roleFilter
      const active = member.isActive !== false
      const matchesStatus = statusFilter === "all" || (statusFilter === "active" ? active : !active)
      return matchesQuery && matchesRole && matchesStatus
    })
  }, [members, query, roleFilter, statusFilter])

  const selectedMember = members.find((member) => member.id === selectedId) || filteredMembers[0]
  const administrators = members.filter((member) => member.role === "admin")
  const pendingInvitations = invitations.filter((invite) => !invite.used)
  const historicalInvitations = invitations.filter((invite) => invite.used)
  const activeMembers = members.filter((member) => member.isActive !== false).length
  const organizationLocation = [organization?.city || user?.location, organization?.country].filter(Boolean).join(", ") || "Location unavailable"
  const organizationSummary = `${organization?.industry || user?.industrySector || "Manufacturing"} organization on PeerLink’s manufacturing knowledge network.`

  const clearFilters = () => {
    setQuery("")
    setRoleFilter("all")
    setStatusFilter("all")
  }

  const sendInvite = async (event: FormEvent) => {
    event.preventDefault()
    if (!isAdmin) return
    setSaving(true)
    setNotice(null)
    try {
      await organizationApi.invite(inviteEmail)
      setInviteEmail("")
      setNotice({ kind: "success", message: "Invitation sent. The link expires according to the live invitation policy." })
      await loadOrganization()
    } catch (err) {
      setNotice({ kind: "error", message: err instanceof Error ? err.message : "Failed to send invitation" })
    } finally {
      setSaving(false)
    }
  }

  const cancelInvite = async (invite: Invitation) => {
    if (!window.confirm(`Cancel invitation for ${invite.email}? This link will no longer be usable.`)) return
    setCancellingId(invite.id)
    setNotice(null)
    try {
      await organizationApi.cancelInvitation(invite.id)
      setNotice({ kind: "success", message: "Invitation cancelled." })
      await loadOrganization()
    } catch (err) {
      setNotice({ kind: "error", message: err instanceof Error ? err.message : "Failed to cancel invitation" })
    } finally {
      setCancellingId(null)
    }
  }

  if (loading) return <div className="px-4 py-8 md:px-8 xl:px-14"><LoadingState title="Loading IIoT Solutions" description="Retrieving the organization profile, roster and permitted administration data." /></div>
  if (error) return <div className="px-4 py-8 md:px-8 xl:px-14"><ErrorState title="Organization unavailable" description={<><span>{error}</span><span className="mt-2 block">No membership or invitation changes were made.</span></>} actionLabel="Retry" onAction={() => void loadOrganization()} /></div>

  const adminTabs: Array<{ id: Exclude<Tab, "roster">; label: string }> = [
    { id: "invitations", label: "Invitations" },
    { id: "permissions", label: "Permissions" },
    { id: "settings", label: "Organization settings" },
  ]

  return (
    <div className="px-4 py-8 md:px-8 xl:px-14">
      <div className="mx-auto w-full max-w-7xl">
        <header className="mb-6 flex flex-col items-start justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <p className="peer-eyebrow mb-2">Verified organization · Manufacturing network</p>
            <h1 className="font-display text-3xl font-semibold tracking-[-0.035em] md:text-4xl">{organizationName}</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--peer-muted)]">
              {isAdmin ? "View the organization workspace and administer the live invitation capabilities available to your account." : "View your organization profile, people, contacts and published knowledge."}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {isAdmin ? <Button onClick={() => setTab("invitations")} className="bg-[var(--peer-teal)] text-white hover:bg-[var(--peer-navy-soft)]"><UserPlus className="size-4" />Invite member</Button> : null}
          </div>
        </header>

        <div className="mb-5 flex gap-3 border-l-4 border-[var(--peer-teal)] bg-[var(--peer-teal-soft)] p-4">
          {isAdmin ? <ShieldCheck className="mt-0.5 size-5 shrink-0 text-[var(--peer-teal)]" /> : <Building2 className="mt-0.5 size-5 shrink-0 text-[var(--peer-teal)]" />}
          <div>
            <p className="text-sm font-semibold">{isAdmin ? "Administrator organization view" : "Member organization view"}</p>
            <p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">
              {isAdmin ? "You see the shared organization workspace plus invitation management and truthful access boundaries for unsupported controls." : "Your organization membership is active. Administration controls are intentionally absent for the Member role."}
            </p>
          </div>
        </div>

        <section className="peer-panel mb-5 grid gap-5 p-5 md:grid-cols-[72px_minmax(0,1fr)_auto] md:items-center md:p-6" aria-labelledby="organization-profile-title">
          <div className="grid size-[72px] place-items-center bg-[var(--peer-navy)] font-display text-xl font-bold text-[#76c5bd]">II</div>
          <div>
            <p className="peer-eyebrow mb-1">Organization profile</p>
            <h2 id="organization-profile-title" className="font-display text-2xl font-semibold">{organizationName}</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--peer-muted)]">{organizationSummary}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="border border-[var(--peer-line)] bg-[#f0eee7] px-2 py-1 text-[10px] font-bold uppercase tracking-wide">Verified organization</span>
              <span className="border border-[var(--peer-line)] bg-[#f0eee7] px-2 py-1 text-[10px] font-bold uppercase tracking-wide">{organization?.industry || user?.industrySector || "Manufacturing"}</span>
              <span className="border border-[var(--peer-line)] bg-[#f0eee7] px-2 py-1 text-[10px] font-bold uppercase tracking-wide">{organizationLocation}</span>
            </div>
          </div>
          <div className="grid gap-2 text-xs text-[var(--peer-muted)] md:justify-items-end">
            <span className="flex items-center gap-2"><Globe2 className="size-4 text-[var(--peer-teal)]" />{organization?.domain || "Domain unavailable"}</span>
            <span className="flex items-center gap-2"><CalendarDays className="size-4 text-[var(--peer-teal)]" />Joined {formatDate(organization?.createdAt)}</span>
            {isAdmin ? <span className="flex items-center gap-2 font-semibold text-[var(--peer-muted)]"><Ban className="size-4" />Profile editing unavailable</span> : null}
          </div>
        </section>

        <section className={`peer-panel mb-5 grid overflow-hidden ${isAdmin ? "grid-cols-2 lg:grid-cols-4" : "grid-cols-2 lg:grid-cols-3"}`} aria-label="Organization summary">
          <Metric label="Organization members" value={members.length} note={`${activeMembers} active`} />
          <Metric label="Administrators & contacts" value={administrators.length} />
          <Metric label="Published use cases" value={useCasesAvailable ? organizationUseCases.length : "—"} />
          {isAdmin ? <Metric label="Pending invitations" value={pendingInvitations.length} /> : null}
        </section>

        <nav className="mb-5 flex gap-2 overflow-x-auto border-b border-[var(--peer-line)]" aria-label="Organization sections">
          <button type="button" onClick={() => setTab("roster")} className={`whitespace-nowrap border-b-2 px-3 py-3 text-xs font-bold ${tab === "roster" ? "border-[var(--peer-teal)] text-[var(--peer-ink)]" : "border-transparent text-[var(--peer-muted)]"}`}>Organization</button>
          {isAdmin ? adminTabs.map((item) => (
            <button key={item.id} type="button" onClick={() => setTab(item.id)} className={`whitespace-nowrap border-b-2 px-3 py-3 text-xs font-bold ${tab === item.id ? "border-[var(--peer-teal)] text-[var(--peer-ink)]" : "border-transparent text-[var(--peer-muted)]"}`}>{item.label}</button>
          )) : null}
        </nav>

        {notice ? (
          <div className={`peer-panel mb-5 flex items-center justify-between border-l-4 p-4 text-sm ${notice.kind === "error" ? "border-l-[var(--peer-danger)]" : "border-l-[var(--peer-teal)]"}`} role="status">
            <span>{notice.message}</span>
            <button type="button" onClick={() => setNotice(null)} aria-label="Dismiss"><X className="size-4" /></button>
          </div>
        ) : null}

        {tab === "roster" ? (
          <>
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
              <main className="min-w-0">
                <section className="peer-panel">
                  <div className="flex flex-col justify-between gap-3 border-b border-[var(--peer-line)] p-5 md:flex-row md:items-end">
                    <div><p className="peer-eyebrow mb-1">Organization roster</p><h2 className="font-display text-xl font-semibold">People at {organizationName}</h2><p className="mt-1 text-xs text-[var(--peer-muted)]">Search the current organization membership and open basic member details.</p></div>
                    <span className="text-xs text-[var(--peer-muted)]">Showing {filteredMembers.length} of {members.length}</span>
                  </div>
                  <div className="grid gap-2 border-b border-[var(--peer-line)] bg-[#f0eee7] p-4 md:grid-cols-[minmax(220px,1fr)_150px_150px]">
                    <label className="relative block">
                      <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-muted)]" />
                      <input className="h-10 w-full border border-[var(--peer-line)] bg-white pl-10 pr-3 text-sm" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search name, email, title or expertise" />
                    </label>
                    <select className="h-10 border border-[var(--peer-line)] bg-white px-3 text-sm" value={roleFilter} onChange={(event) => setRoleFilter(event.target.value as RoleFilter)} aria-label="Filter members by role"><option value="all">All roles</option><option value="admin">Administrators</option><option value="member">Members</option></select>
                    <select className="h-10 border border-[var(--peer-line)] bg-white px-3 text-sm" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as StatusFilter)} aria-label="Filter members by status"><option value="all">All statuses</option><option value="active">Active</option><option value="inactive">Inactive</option></select>
                  </div>
                  {members.length === 0 ? (
                    <EmptyState className="m-5 min-h-64 shadow-none" title="Your organization has no members yet" description={isAdmin ? "Use the invitation section to invite the first verified company colleague." : "Contact an organization administrator if you expected to see colleagues here."} actionLabel={isAdmin ? "Open invitations" : undefined} onAction={isAdmin ? () => setTab("invitations") : undefined} />
                  ) : filteredMembers.length === 0 ? (
                    <EmptyState className="m-5 min-h-64 shadow-none" title="No members match these filters" description="Try a different name, email, role or status. Organization membership has not changed." actionLabel="Clear filters" onAction={clearFilters} />
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full min-w-[760px] text-left text-sm">
                        <thead className="bg-[#f0eee7] text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--peer-muted)]"><tr><th className="px-5 py-3">Member</th><th className="px-5 py-3">Position</th><th className="px-5 py-3">Role</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Details</th>{isAdmin ? <th className="px-5 py-3">Admin actions</th> : null}</tr></thead>
                        <tbody>
                          {filteredMembers.map((member) => (
                            <tr key={member.id} className={`border-b border-[var(--peer-line)] last:border-b-0 ${selectedMember?.id === member.id ? "bg-[var(--peer-teal-soft)]/50" : "hover:bg-white"}`}>
                              <td className="px-5 py-4"><div className="flex min-w-[210px] items-center gap-3"><Avatar name={memberName(member)} src={member.profilePictureUrl} /><div className="min-w-0"><p className="truncate font-semibold">{memberName(member)}</p><p className="truncate text-xs text-[var(--peer-muted)]">{member.email}</p></div></div></td>
                              <td className="px-5 py-4 text-xs text-[var(--peer-muted)]">{member.title || "Team member"}</td>
                              <td className="px-5 py-4"><span className={`inline-flex border px-2 py-1 text-[10px] font-bold uppercase ${member.role === "admin" ? "border-[#c4d7d1] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]" : "border-[var(--peer-line)]"}`}>{member.role === "admin" ? "Administrator" : "Member"}</span></td>
                              <td className="px-5 py-4"><span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${member.isActive === false ? "text-[var(--peer-danger)]" : "text-[var(--peer-teal)]"}`}><span className="size-1.5 rounded-full bg-current" />{member.isActive === false ? "Inactive" : "Active"}</span></td>
                              <td className="px-5 py-4"><button type="button" onClick={() => setSelectedId(member.id)} className="inline-flex items-center gap-1 text-xs font-bold text-[var(--peer-blue)]">View details <ArrowRight className="size-3.5" /></button></td>
                              {isAdmin ? <td className="px-5 py-4"><button type="button" disabled title="No member mutation API is available" className="grid size-8 place-items-center border border-[var(--peer-line)] text-[var(--peer-muted)] opacity-60"><MoreHorizontal className="size-4" /></button></td> : null}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </section>
              </main>

              <aside className="grid h-fit gap-5 xl:sticky xl:top-[calc(var(--peer-topbar-height)+24px)]">
                <section className="peer-panel">
                  <div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Member detail</p><h2 className="font-display text-xl font-semibold">Profile and access</h2></div>
                  {selectedMember ? (
                    <div className="p-5">
                      <div className="flex items-center gap-3"><Avatar name={memberName(selectedMember)} src={selectedMember.profilePictureUrl} size="lg" /><div><p className="font-semibold">{memberName(selectedMember)}</p><p className="text-sm text-[var(--peer-muted)]">{selectedMember.title || "Team member"}</p></div></div>
                      <dl className="mt-5 grid gap-4 text-sm">
                        <div><dt className="text-[10px] font-bold uppercase text-[var(--peer-muted)]">Organization membership</dt><dd className="mt-1">{organizationName} · {selectedMember.role === "admin" ? "Administrator" : "Member"}</dd></div>
                        <div><dt className="text-[10px] font-bold uppercase text-[var(--peer-muted)]">Contact</dt><dd className="mt-1 break-all">{selectedMember.email}</dd></div>
                        <div><dt className="text-[10px] font-bold uppercase text-[var(--peer-muted)]">Location</dt><dd className="mt-1">{selectedMember.location || organizationLocation}</dd></div>
                        <div><dt className="text-[10px] font-bold uppercase text-[var(--peer-muted)]">Joined</dt><dd className="mt-1">{formatDate(selectedMember.createdAt)}</dd></div>
                        <div><dt className="text-[10px] font-bold uppercase text-[var(--peer-muted)]">Status</dt><dd className="mt-1">{selectedMember.isActive === false ? "Inactive" : "Active"}</dd></div>
                      </dl>
                      <Button asChild className="mt-5 w-full bg-[var(--peer-teal)] text-white hover:bg-[var(--peer-navy-soft)]"><a href={`mailto:${selectedMember.email}`}><Mail className="size-4" />Email member</a></Button>
                      {isAdmin ? <div className="mt-5 border-t border-[var(--peer-line)] pt-4"><p className="text-xs font-semibold">Administrative controls</p><p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">Role changes, suspension and removal are not exposed by the current backend. No simulated action is offered.</p><div className="mt-3 grid gap-2"><Button variant="outline" disabled className="justify-start bg-white"><UserCog className="size-4" />Change role unavailable</Button><Button variant="outline" disabled className="justify-start bg-white"><Ban className="size-4" />Suspend unavailable</Button></div></div> : null}
                    </div>
                  ) : <EmptyState className="m-5 min-h-56 shadow-none" title="Select a member" description="Choose a roster row to inspect basic organization membership details." />}
                </section>

                <section className="peer-panel">
                  <div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Administrators & contacts</p><h2 className="font-display text-lg font-semibold">Who to contact</h2></div>
                  {administrators.length ? administrators.map((administrator) => (
                    <div key={administrator.id} className="border-b border-[var(--peer-line)] p-5 last:border-b-0"><div className="flex items-center gap-3"><Avatar name={memberName(administrator)} src={administrator.profilePictureUrl} /><div><p className="text-sm font-semibold">{memberName(administrator)}</p><p className="text-xs text-[var(--peer-muted)]">{administrator.title || "Organization administrator"}</p></div></div><a className="mt-3 inline-flex items-center gap-2 text-xs font-bold text-[var(--peer-blue)]" href={`mailto:${administrator.email}`}><Mail className="size-3.5" />Contact administrator</a></div>
                  )) : <p className="p-5 text-sm text-[var(--peer-muted)]">No administrator contact was returned by the organization roster.</p>}
                </section>
              </aside>
            </div>

            <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(300px,.65fr)]">
              <section className="peer-panel">
                <div className="flex items-start justify-between gap-4 border-b border-[var(--peer-line)] p-5"><div><p className="peer-eyebrow mb-1">Organization knowledge</p><h2 className="font-display text-xl font-semibold">Use cases from {organizationName}</h2><p className="mt-1 text-xs text-[var(--peer-muted)]">Published work matched to the live organization name.</p></div><Button asChild variant="outline" className="shrink-0 bg-white"><Link to="/usecases">View all</Link></Button></div>
                {!useCasesAvailable ? <p className="p-5 text-sm leading-6 text-[var(--peer-muted)]">The use-case service could not be reached. No representative organization stories are being substituted.</p> : organizationUseCases.length === 0 ? <EmptyState className="m-5 min-h-48 shadow-none" title="No published organization use cases" description="Use cases will appear here when the live library returns items published by this organization." /> : <div>{organizationUseCases.map((item) => <Link key={item.id} to={`/usecases/${item.company_slug}/${item.title_slug}`} className="grid grid-cols-[38px_minmax(0,1fr)_auto] items-center gap-3 border-b border-[var(--peer-line)] p-5 last:border-b-0 hover:bg-white"><span className="grid size-[38px] place-items-center bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><Factory className="size-4" /></span><span className="min-w-0"><strong className="block truncate text-sm">{item.title}</strong><span className="mt-1 block text-xs text-[var(--peer-muted)]">{item.category} · {item.views || 0} views</span></span><ArrowRight className="size-4 text-[var(--peer-muted)]" /></Link>)}</div>}
              </section>
              <section className="peer-panel">
                <div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Recent organization activity</p><h2 className="font-display text-xl font-semibold">Truthful boundary</h2></div>
                <div className="p-5"><Clock3 className="mb-3 size-5 text-[var(--peer-teal)]" /><p className="text-sm font-semibold">Organization activity feed unavailable</p><p className="mt-2 text-xs leading-5 text-[var(--peer-muted)]">The current backend does not expose an organization-scoped activity endpoint. Personal or network activity is not shown here as if it belonged to {organizationName}.</p></div>
              </section>
            </div>

            {isAdmin ? <section className="peer-panel mt-5"><div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Administrator controls</p><h2 className="font-display text-xl font-semibold">Organization administration</h2><p className="mt-1 text-xs text-[var(--peer-muted)]">Available and unsupported capabilities remain clearly separated.</p></div><div className="grid sm:grid-cols-2 lg:grid-cols-4"><button type="button" onClick={() => setTab("invitations")} className="min-h-36 border-b border-r border-[var(--peer-line)] p-5 text-left hover:bg-white"><Mail className="mb-4 size-5 text-[var(--peer-teal)]" /><strong className="block text-sm">Invitations</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">Send invitations and cancel pending links.</span></button><button type="button" onClick={() => setTab("permissions")} className="min-h-36 border-b border-r border-[var(--peer-line)] p-5 text-left hover:bg-white"><ShieldCheck className="mb-4 size-5 text-[var(--peer-teal)]" /><strong className="block text-sm">Roles & permissions</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">Review the enforced role boundary.</span></button><button type="button" onClick={() => setTab("settings")} className="min-h-36 border-b border-r border-[var(--peer-line)] p-5 text-left hover:bg-white"><Building2 className="mb-4 size-5 text-[var(--peer-teal)]" /><strong className="block text-sm">Organization settings</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">Inspect verified read-only profile data.</span></button><div className="min-h-36 border-b p-5"><UserCog className="mb-4 size-5 text-[var(--peer-muted)]" /><strong className="block text-sm">Member controls</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">Role, suspend and remove APIs are unavailable.</span></div></div></section> : null}
          </>
        ) : null}

        {tab === "invitations" ? (
          isAdmin ? (
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
              <div className="grid gap-5">
                <section className="peer-panel">
                  <div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Awaiting response</p><h2 className="font-display text-xl font-semibold">Pending invitations</h2><p className="mt-1 text-xs text-[var(--peer-muted)]">Live invitation records returned for this organization.</p></div>
                  {pendingInvitations.length === 0 ? <EmptyState className="m-5 min-h-56 shadow-none" title="No pending invitations" description="All invitations have been accepted, cancelled or expired." /> : pendingInvitations.map((invite) => (
                    <div key={invite.id} className="grid gap-3 border-b border-[var(--peer-line)] p-5 last:border-b-0 md:grid-cols-[minmax(0,1fr)_auto] md:items-center"><div><p className="font-semibold">{invite.email}</p><p className="mt-1 text-xs text-[var(--peer-muted)]">Sent by {invite.invited_by_name || invite.invited_by_email || "Administrator"} · Created {formatDate(invite.created_at)} · Expires {formatDate(invite.expires_at)}</p></div><div className="flex items-center gap-2"><span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#a15b1b]"><Clock3 className="size-3.5" />Pending</span><Button disabled variant="outline" title="No resend endpoint is available" className="bg-white">Resend unavailable</Button><Button variant="outline" disabled={cancellingId === invite.id} onClick={() => void cancelInvite(invite)} className="bg-white text-[var(--peer-danger)]">{cancellingId === invite.id ? "Cancelling…" : "Cancel"}</Button></div></div>
                  ))}
                </section>
                <section className="peer-panel">
                  <div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Invitation history</p><h2 className="font-display text-xl font-semibold">Accepted invitations</h2></div>
                  {historicalInvitations.length === 0 ? <p className="p-5 text-sm text-[var(--peer-muted)]">No accepted invitations were returned.</p> : historicalInvitations.map((invite) => <div key={invite.id} className="grid gap-2 border-b border-[var(--peer-line)] p-5 last:border-b-0 md:grid-cols-[1fr_auto]"><div><p className="font-semibold">{invite.email}</p><p className="mt-1 text-xs text-[var(--peer-muted)]">Invited {formatDate(invite.created_at)} · Accepted {formatDate(invite.used_at)}</p></div><span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[var(--peer-teal)]"><CheckCircle2 className="size-4" />Accepted</span></div>)}
                </section>
              </div>
              <aside className="peer-panel h-fit xl:sticky xl:top-[calc(var(--peer-topbar-height)+24px)]">
                <div className="bg-[var(--peer-navy)] p-5 text-white"><p className="text-[10px] font-bold uppercase tracking-[0.13em] text-[#76c5bd]">Invite member</p><h2 className="font-display mt-1 text-xl font-semibold">Company-domain invitation</h2><p className="mt-2 text-xs leading-5 text-[#b8cdca]">The current API accepts one email address. Display name, team, custom message and role selection are not sent because the backend has no contract for them.</p></div>
                <form onSubmit={sendInvite} className="grid gap-4 p-5"><div><label htmlFor="invite-email" className="text-xs font-bold">Company email address</label><input id="invite-email" type="email" required className="mt-2 h-11 w-full border border-[var(--peer-line)] bg-white px-3 text-sm" placeholder={`name@${organization?.domain || "company.com"}`} value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} /><p className="mt-2 text-[11px] leading-5 text-[var(--peer-muted)]">Backend validation enforces the verified organization domain and seven-day invitation behavior.</p></div><div className="border border-[var(--peer-line)] bg-[#f0eee7] p-4"><p className="text-[10px] font-bold uppercase text-[var(--peer-muted)]">Access preview</p><p className="mt-2 text-sm font-semibold">Member — standard organization access</p><p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">Administrator invitation selection is not exposed by the current send endpoint.</p></div><Button disabled={saving} className="bg-[var(--peer-teal)] text-white hover:bg-[var(--peer-navy-soft)]"><UserPlus className="size-4" />{saving ? "Sending…" : "Send invitation"}</Button></form>
              </aside>
            </div>
          ) : <AccessDeniedState title="Invitations are administrator-only" description="Members can view the organization roster, contacts and knowledge, but cannot open invitation administration." />
        ) : null}

        {tab === "permissions" ? (
          isAdmin ? <section className="peer-panel"><div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Organization access model</p><h2 className="font-display text-xl font-semibold">Roles and permissions</h2><p className="mt-1 text-xs leading-5 text-[var(--peer-muted)]">This matrix documents current behavior. It is not editable because the backend does not expose permission-policy mutations.</p></div><div className="hidden grid-cols-[minmax(0,1fr)_140px_140px] border-b border-[var(--peer-line)] bg-[#f0eee7] px-5 py-3 text-[10px] font-bold uppercase tracking-wide text-[var(--peer-muted)] md:grid"><span>Capability</span><span>Member</span><span>Administrator</span></div><Capability title="View organization profile and roster" description="Inspect shared membership, contacts and published organization knowledge." member administrator /><Capability title="Use the wider People discovery surface" description="Discover collaborators across PeerLink outside this organization workspace." member administrator /><Capability title="Send and cancel invitations" description="Create domain-validated invitations and cancel pending links." member={false} administrator /><Capability title="Change roles, suspend or remove members" description="The current backend exposes no mutation contract for these controls." member={false} administrator={false} /><Capability title="Edit organization settings" description="Verified organization data is read-only in the current API." member={false} administrator={false} /><div className="flex gap-3 border-t border-[var(--peer-line)] bg-[var(--peer-teal-soft)] p-5"><Shield className="mt-0.5 size-5 shrink-0 text-[var(--peer-teal)]" /><p className="text-xs leading-5 text-[var(--peer-muted)]"><strong className="text-[var(--peer-ink)]">Separation principle:</strong> this is the IIoT Solutions organization workspace. People remains the broader collaboration and discovery surface.</p></div></section> : <AccessDeniedState title="Permissions are administrator-only" description="Your Member role can view shared organization information, but not organization access administration." />
        ) : null}

        {tab === "settings" ? (
          isAdmin ? <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]"><section className="peer-panel"><div className="border-b border-[var(--peer-line)] p-5"><p className="peer-eyebrow mb-1">Administrator settings</p><h2 className="font-display text-xl font-semibold">Verified organization information</h2><p className="mt-1 text-xs text-[var(--peer-muted)]">Current live profile fields are displayed without simulated editing.</p></div><dl className="grid sm:grid-cols-2"><DetailRow label="Organization" value={organizationName} /><DetailRow label="Verified domain" value={organization?.domain} /><DetailRow label="Industry" value={organization?.industry || user?.industrySector} /><DetailRow label="Organization size" value={organization?.size} /><DetailRow label="Country" value={organization?.country} /><DetailRow label="City" value={organization?.city || user?.location} /><DetailRow label="Default invitation role" value="Member (current endpoint behavior)" /><DetailRow label="Organization status" value={organization?.isActive === false ? "Inactive" : "Active"} /></dl></section><aside className="peer-panel h-fit p-5"><Building2 className="mb-3 size-5 text-[var(--peer-teal)]" /><p className="font-semibold">Settings are read-only</p><p className="mt-2 text-sm leading-6 text-[var(--peer-muted)]">The backend returns organization profile data but does not expose update endpoints for the profile, default role, domain policy or join notifications.</p><Button disabled variant="outline" className="mt-4 w-full bg-white"><Shield className="size-4" />Save settings unavailable</Button></aside></div> : <AccessDeniedState title="Organization settings are administrator-only" description="Members can view the shared organization profile, but cannot open administrator settings." />
        ) : null}
      </div>
    </div>
  )
}

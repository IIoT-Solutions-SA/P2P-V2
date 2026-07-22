import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { Building2, Factory, Mail, MapPin, MessageSquare, Search, Send, UserPlus, Users, X } from "lucide-react"
import { Avatar } from "@/components/ui/Avatar"
import { Button } from "@/components/ui/button"
import { AccessDeniedState, EmptyState, ErrorState, LoadingState } from "@/components/shared/AppState"
import { peopleApi, type OrganizationMember } from "@/lib/api/people"
import { useAuth } from "@/contexts/AuthContext"
import { formatOrganizationName } from "@/lib/formatters"
import { cn } from "@/lib/utils"

const memberName = (member: OrganizationMember) =>
  member.name || `${member.firstName || ""} ${member.lastName || ""}`.trim() || member.email

const normalize = (value?: string) => (value || "").toLowerCase().trim()

export default function Connect() {
  const { user, organization } = useAuth()
  const [people, setPeople] = useState<OrganizationMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState("")
  const [company, setCompany] = useState("all")
  const [location, setLocation] = useState("all")
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const loadPeople = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await peopleApi.directory()
      const directory = data.users || []
      setPeople(directory)
      setSelectedId((current) => current || directory.find((person) => !person.isCurrentOrganization)?.id || null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load the PeerLink directory")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadPeople()
  }, [])

  const networkPeople = useMemo(() => people.filter((person) => !person.isCurrentOrganization), [people])
  const organizationPeopleCount = people.length - networkPeople.length
  const companyOptions = useMemo(
    () => Array.from(new Set(networkPeople.map((person) => person.company).filter((value): value is string => Boolean(value)))).sort(),
    [networkPeople],
  )
  const locationOptions = useMemo(
    () => Array.from(new Set(networkPeople.map((person) => person.location).filter((value): value is string => Boolean(value)))).sort(),
    [networkPeople],
  )

  const filteredPeople = useMemo(() => {
    const needle = normalize(query)
    return networkPeople.filter((person) => {
      const searchable = [
        memberName(person),
        person.title,
        person.company,
        person.location,
        person.industrySector,
      ].map((item) => normalize(item)).join(" ")
      return (!needle || searchable.includes(needle))
        && (company === "all" || person.company === company)
        && (location === "all" || person.location === location)
    })
  }, [company, location, networkPeople, query])

  const selectedPerson = filteredPeople.find((person) => person.id === selectedId)
    || filteredPeople[0]
  const currentOrganizationName = formatOrganizationName(organization?.name || user?.company, "Your organization")
  const hasFilters = Boolean(query || company !== "all" || location !== "all")

  const clearFilters = () => {
    setQuery("")
    setCompany("all")
    setLocation("all")
  }

  if (!user) return <AccessDeniedState title="Sign in required" description="People discovery is available to authenticated PeerLink members." />
  if (loading) return <div className="px-5 py-10 md:px-8 xl:px-[58px]"><LoadingState title="Loading PeerLink people" /></div>
  if (error) return <div className="px-5 py-10 md:px-8 xl:px-[58px]"><ErrorState title="People directory unavailable" description={error} actionLabel="Retry" onAction={() => void loadPeople()} /></div>

  return (
    <div className="min-h-[calc(100vh-var(--peer-topbar-height))] bg-[var(--peer-paper)] [--peer-surface:#ffffff]">
      <div className="mx-auto w-full max-w-[1430px] px-5 pb-16 pt-8 md:px-8 md:pt-11 xl:px-[58px]">
        <header className="mb-8 grid items-end gap-5 md:grid-cols-[minmax(0,1fr)_auto] md:gap-7">
          <div>
            <p className="peer-eyebrow mb-2">People · Shared network directory</p>
            <h1 className="font-display max-w-[820px] text-[clamp(30px,3.2vw,44px)] font-semibold leading-[1.13] tracking-[-0.045em]">Find manufacturing peers by organization, industry, and location.</h1>
            <p className="mt-3 max-w-[800px] text-[15px] leading-6 text-[var(--peer-muted)]">Discover collaborators across PeerLink. Your own membership, invitations, permissions, and administration remain in the dedicated {currentOrganizationName} workspace.</p>
          </div>
          <div className="min-w-[235px] border-l-2 border-[var(--peer-teal)] py-1 pl-4">
            <strong className="font-display block text-xl font-semibold">{networkPeople.length} people to connect with</strong>
            <span className="text-xs text-[var(--peer-muted)]">{organizationPeopleCount} organization members are listed separately</span>
          </div>
        </header>

        <div className="grid items-start gap-[22px] xl:grid-cols-[minmax(0,1.55fr)_minmax(330px,0.85fr)]">
          <section className="peer-panel min-w-0" aria-labelledby="directory-title">
            <div className="flex items-start justify-between border-b border-[var(--peer-line)] px-6 py-5">
              <div><p className="peer-eyebrow mb-1">Network discovery</p><h2 id="directory-title" className="font-display text-xl font-semibold">People outside your organization</h2></div>
              <span className="text-xs text-[var(--peer-muted)]">{filteredPeople.length} shown</span>
            </div>

            <div className="grid gap-2 border-b border-[var(--peer-line)] bg-[#f7f5ee] p-5 lg:grid-cols-[minmax(240px,1fr)_repeat(2,minmax(170px,0.55fr))]">
              <label className="relative block"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-teal)]" /><input value={query} onChange={(event) => setQuery(event.target.value)} className="h-11 w-full border border-[var(--peer-line)] bg-white pl-10 pr-3 text-sm" placeholder="Search people, organizations, industries" /></label>
              <label className="relative block"><Building2 className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-teal)]" /><select value={company} onChange={(event) => setCompany(event.target.value)} className="h-11 w-full appearance-none border border-[var(--peer-line)] bg-white pl-10 pr-3 text-sm"><option value="all">All organizations</option>{companyOptions.map((item) => <option key={item}>{formatOrganizationName(item, item)}</option>)}</select></label>
              <label className="relative block"><MapPin className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-teal)]" /><select value={location} onChange={(event) => setLocation(event.target.value)} className="h-11 w-full appearance-none border border-[var(--peer-line)] bg-white pl-10 pr-3 text-sm"><option value="all">All locations</option>{locationOptions.map((item) => <option key={item}>{item}</option>)}</select></label>
            </div>

            {hasFilters ? <div className="flex flex-wrap items-center gap-2 border-b border-[var(--peer-line)] px-5 py-3">{company !== "all" ? <span className="bg-[var(--peer-teal-soft)] px-2.5 py-1.5 text-xs font-bold text-[var(--peer-teal)]">{formatOrganizationName(company, company)}</span> : null}{location !== "all" ? <span className="bg-[var(--peer-teal-soft)] px-2.5 py-1.5 text-xs font-bold text-[var(--peer-teal)]">{location}</span> : null}<button type="button" onClick={clearFilters} className="inline-flex items-center gap-1 border border-[var(--peer-line)] px-2.5 py-1.5 text-xs font-semibold text-[var(--peer-muted)]"><X className="size-3.5" />Clear filters</button></div> : null}

            {filteredPeople.length === 0 ? (hasFilters ? <EmptyState className="m-5 min-h-64 shadow-none" title="No people match those filters" description="Clear one filter or broaden the organization and location to see more manufacturing peers." actionLabel="Reset filters" onAction={clearFilters} /> : <div className="m-5 grid min-h-64 place-items-center border border-dashed border-[var(--peer-line)] bg-[#f7f5ee] p-8 text-center"><div><span className="mx-auto mb-4 grid size-12 place-items-center rounded-full bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><Users className="size-5" /></span><h3 className="font-display text-lg font-semibold">No external PeerLink people yet</h3><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[var(--peer-muted)]">There are currently zero registered people outside {currentOrganizationName}. Your {organizationPeopleCount} organization members are managed in the organization workspace, not shown here as new connections.</p><Link to="/organization" className="mt-5 inline-flex h-10 items-center border border-[var(--peer-line)] bg-white px-4 text-xs font-bold text-[var(--peer-navy)]">View {currentOrganizationName} members</Link></div></div>) : (
              <div>
                {filteredPeople.map((person) => {
                  const name = memberName(person)
                  const active = selectedPerson?.id === person.id
                  return (
                    <button key={person.id} type="button" onClick={() => setSelectedId(person.id)} className={cn("grid w-full gap-4 border-b border-[var(--peer-line)] px-5 py-[18px] text-left last:border-b-0 hover:bg-[#f2f5f1] sm:grid-cols-[48px_minmax(0,1fr)_auto]", active && "bg-[#eef3ee] shadow-[inset_3px_0_0_var(--peer-teal)]")}>
                      <Avatar name={name} src={person.profilePictureUrl} size="lg" />
                      <span className="min-w-0"><span className="flex flex-wrap items-center gap-2"><strong className="font-display truncate text-[15px]">{name}</strong><span className="bg-[var(--peer-teal-soft)] px-2 py-0.5 text-[10px] font-bold uppercase text-[var(--peer-teal)]">Network peer</span></span><span className="mt-1 block text-xs text-[var(--peer-muted)]">{person.title || "Manufacturing professional"} · {formatOrganizationName(person.company, "Independent")}</span><span className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-[var(--peer-muted)]"><span className="inline-flex items-center gap-1"><MapPin className="size-3.5 text-[var(--peer-teal)]" />{person.location || "Location unavailable"}</span><span className="inline-flex items-center gap-1"><Factory className="size-3.5 text-[var(--peer-teal)]" />{person.industrySector || "Manufacturing"}</span></span></span>
                      <span className="flex gap-2 self-center"><span className="grid size-9 place-items-center border border-[var(--peer-line)] bg-white"><Users className="size-4" /></span><span className="grid size-9 place-items-center border border-[var(--peer-line)] bg-white"><Send className="size-4" /></span></span>
                    </button>
                  )
                })}
              </div>
            )}
          </section>

          <aside className="peer-panel overflow-hidden xl:sticky xl:top-[calc(var(--peer-topbar-height)+22px)]" aria-labelledby="profile-preview-title">
            {selectedPerson ? <>
              <div className="bg-[var(--peer-navy)] p-6 text-white"><div className="flex items-center gap-4"><Avatar name={memberName(selectedPerson)} src={selectedPerson.profilePictureUrl} size="lg" /><div className="min-w-0"><h2 id="profile-preview-title" className="font-display truncate text-[22px] font-semibold">{memberName(selectedPerson)}</h2><p className="mt-1 text-xs text-[#9cb4b5]">{selectedPerson.title || "Manufacturing professional"} · {formatOrganizationName(selectedPerson.company, "Independent")}</p></div></div><div className="mt-5 inline-flex items-center gap-2 text-xs font-bold text-[#d8ece8]"><span className="size-2 rounded-full bg-[#1b8f75]" />Available for collaborator requests</div><p className="mt-4 text-[13px] leading-6 text-[#b8cbca]">Connect around practical manufacturing work, industry context, and implementation lessons across the PeerLink network.</p></div>
              <div className="grid grid-cols-2 gap-2 border-b border-[var(--peer-line)] p-5"><Button asChild className="bg-[var(--peer-blue)] text-white"><a href={`mailto:${selectedPerson.email}`}><UserPlus className="size-4" />Collaborate</a></Button><Button variant="outline" asChild className="bg-white"><a href={`mailto:${selectedPerson.email}`}><MessageSquare className="size-4" />Contact</a></Button></div>
              <dl className="px-5">{[["Organization", formatOrganizationName(selectedPerson.company, "Independent")], ["Location", selectedPerson.location || "Not provided"], ["Industry", selectedPerson.industrySector || "Manufacturing"]].map(([label, value]) => <div key={label} className="grid grid-cols-[105px_1fr] gap-3 border-b border-[var(--peer-line)] py-4 last:border-b-0"><dt className="text-[11px] text-[var(--peer-muted)]">{label}</dt><dd className="font-display text-[13px] font-bold">{value}</dd></div>)}</dl>
              <div className="flex items-start gap-2 border-t border-[var(--peer-line)] bg-[#f1f2ed] px-5 py-4 text-[11px] leading-5 text-[var(--peer-muted)]"><Mail className="mt-0.5 size-4 shrink-0 text-[var(--peer-teal)]" /><span>People is the shared network directory. Invitation, role, removal, and organization controls remain under {currentOrganizationName}.</span></div>
            </> : <EmptyState className="m-5 min-h-72 shadow-none" title="Select a person" description="Choose a directory row to inspect collaboration context." />}
          </aside>

          {selectedPerson ? <section className="peer-panel overflow-hidden xl:col-span-2" aria-labelledby="profile-context-title"><div className="grid lg:grid-cols-[minmax(0,1.3fr)_minmax(300px,0.7fr)]"><div className="bg-[var(--peer-navy)] px-7 py-8 text-white md:px-9"><p className="peer-eyebrow !text-[#76c5bd]">Profile context</p><h2 id="profile-context-title" className="font-display my-3 max-w-[720px] text-[clamp(23px,2.6vw,33px)] font-semibold leading-tight">A complete peer profile keeps collaboration focused on work context.</h2><p className="max-w-[720px] text-[13px] leading-6 text-[#b8cdca]">Organization, industry, role, and location help members identify the right person without exposing organization-administration controls in the network directory.</p></div><div className="grid content-center gap-4 bg-[#e1e7e2] p-7"><div className="flex gap-3"><Building2 className="size-5 shrink-0 text-[var(--peer-teal)]" /><span><strong className="block text-sm">Organization context</strong><span className="text-xs text-[var(--peer-muted)]">{formatOrganizationName(selectedPerson.company, "Independent peer")}</span></span></div><div className="flex gap-3"><MapPin className="size-5 shrink-0 text-[var(--peer-teal)]" /><span><strong className="block text-sm">Working location</strong><span className="text-xs text-[var(--peer-muted)]">{selectedPerson.location || "Not provided"}</span></span></div><div className="flex gap-3"><Factory className="size-5 shrink-0 text-[var(--peer-teal)]" /><span><strong className="block text-sm">Manufacturing focus</strong><span className="text-xs text-[var(--peer-muted)]">{selectedPerson.industrySector || "General manufacturing"}</span></span></div></div></div></section> : null}
        </div>
      </div>
    </div>
  )
}

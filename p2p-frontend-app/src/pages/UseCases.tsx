import { useCallback, useEffect, useMemo, useState, type ElementType } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  Activity,
  ArrowRight,
  ArrowUpDown,
  Bookmark,
  Bot,
  CheckCircle2,
  Eye,
  Factory,
  FileText,
  Gauge,
  ScanEye,
  Search,
  ThumbsUp,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/AppState"
import { useCasesApi, type UseCaseListItem } from "@/lib/api/usecases"

const sortOptions = [
  { id: "newest", label: "Newest" },
  { id: "most_viewed", label: "Most viewed" },
  { id: "most_liked", label: "Most liked" },
]

const categoryIcons: ElementType[] = [Bot, Gauge, ScanEye]
const categoryDescriptions = [
  "Robotics, PLC upgrades, cells and commissioning.",
  "Utilities, plant efficiency and energy optimization.",
  "Inspection, traceability and defect reduction.",
]

const splitBenefits = (value?: string) =>
  [...new Set((value || "").split(";").map((item) => item.trim()).filter(Boolean))].slice(0, 2)

const isStructuredMetric = (value: string) => {
  const compact = value.replace(/\s+/g, " ").trim()
  return compact.length <= 90 && compact.split(" ").length <= 12 && /\d/.test(compact)
}

const displayMetrics = (value?: string) => splitBenefits(value).filter(isStructuredMetric)

const benefitParts = (value: string) => {
  const compact = value.replace(/\s+/g, " ").trim()
  const match = compact.match(/^((?:SAR\s+)?[\d,.]+(?:%|x|[KMB])?)(?:\s+(.+))?$/i)
  return match
    ? { headline: match[1], label: match[2] || "Measured impact" }
    : { headline: "Impact", label: compact }
}

const compactSummary = (value?: string, maxLength = 140) => {
  const compact = (value || "").replace(/\s+/g, " ").trim()
  if (!compact) return "Open this implementation to review its challenge, approach, and outcomes."
  return compact.length > maxLength ? `${compact.slice(0, maxLength - 1).trimEnd()}…` : compact
}

export default function UseCases() {
  const navigate = useNavigate()
  const [categories, setCategories] = useState<Array<{ id: string; name: string; count: number }>>([])
  const [items, setItems] = useState<UseCaseListItem[]>([])
  const [stats, setStats] = useState<{ totalUseCases: number; contributingCompanies: number; successStories: number } | null>(null)
  const [bookmarked, setBookmarked] = useState<Set<string>>(new Set())
  const [liked, setLiked] = useState<Set<string>>(new Set())
  const [category, setCategory] = useState("all")
  const [query, setQuery] = useState("")
  const [sortBy, setSortBy] = useState("newest")
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const limit = 10

  const loadLibrary = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [categoryData, listData, statsData, bookmarkData] = await Promise.all([
        useCasesApi.categories(),
        useCasesApi.list({ category, search: query, sortBy, limit, skip: (page - 1) * limit }),
        useCasesApi.stats().catch(() => null),
        useCasesApi.bookmarks().catch(() => []),
      ])
      setCategories(categoryData || [])
      setItems(listData.items || [])
      setTotal(listData.total || 0)
      setStats(statsData)
      setBookmarked(new Set((bookmarkData || []).map((item) => String(item.id))))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load use cases")
    } finally {
      setLoading(false)
    }
  }, [category, page, query, sortBy])

  useEffect(() => {
    const id = window.setTimeout(() => void loadLibrary(), 250)
    return () => window.clearTimeout(id)
  }, [loadLibrary])

  useEffect(() => setPage(1), [category, query, sortBy])
  useEffect(() => window.scrollTo({ top: 0, behavior: "smooth" }), [page])

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / limit)), [total])
  const activeCategory = categories.find((item) => item.id === category)
  const featuredItems = items.filter((item) => item.featured).slice(0, 3)
  const visibleCategories = categories.filter((item) => item.id !== "all").slice(0, 3)

  const toggleLike = async (item: UseCaseListItem) => {
    try {
      const result = await useCasesApi.like(item.company_slug, item.title_slug)
      setItems((prev) => prev.map((entry) => entry.id === item.id ? { ...entry, likes: result.likes } : entry))
      setLiked((prev) => {
        const next = new Set(prev)
        if (result.liked) next.add(item.id)
        else next.delete(item.id)
        return next
      })
    } catch {
      // Keep the current library intact when an authenticated action is rejected.
    }
  }

  const toggleBookmark = async (item: UseCaseListItem) => {
    try {
      const result = await useCasesApi.bookmark(item.company_slug, item.title_slug)
      setItems((prev) => prev.map((entry) => entry.id === item.id ? { ...entry, saves: result.bookmarks } : entry))
      setBookmarked((prev) => {
        const next = new Set(prev)
        if (result.bookmarked) next.add(item.id)
        else next.delete(item.id)
        return next
      })
    } catch {
      // Authentication and API error handling remain owned by the existing client/session layer.
    }
  }

  if (loading && items.length === 0) {
    return <div className="px-4 py-8 md:px-8 xl:px-14"><LoadingState title="Loading use cases" description="Retrieving use cases, filters, metrics, and your saved library context." /></div>
  }
  if (error) {
    return <div className="px-4 py-8 md:px-8 xl:px-14"><ErrorState title="Could not load the library" description={error} actionLabel="Try again" onAction={() => void loadLibrary()} /></div>
  }

  return (
    <main className="mx-auto w-full max-w-[1430px] px-4 py-8 md:px-8 md:py-11 xl:px-14">
      <header className="mb-8 grid items-end gap-7 lg:grid-cols-[minmax(0,1fr)_auto]">
        <div>
          <p className="peer-eyebrow mb-2">Manufacturing knowledge library</p>
          <h1 className="max-w-4xl font-display text-3xl font-semibold tracking-[-0.04em] sm:text-4xl xl:text-[45px] xl:leading-[1.13]">Explore proven manufacturing implementations.</h1>
          <p className="mt-3 max-w-3xl text-[15px] leading-6 text-[var(--peer-muted)]">Search practical projects from Saudi manufacturing teams, compare measurable outcomes, and connect with the people behind the work.</p>
        </div>
        <Button asChild className="h-10 rounded-none bg-[var(--peer-navy)] px-4 text-xs font-bold text-white hover:bg-[#174550]">
          <Link to="/submit"><FileText className="size-4" />Submit use case</Link>
        </Button>
      </header>

      <section className="peer-panel mb-[22px] overflow-hidden" aria-labelledby="library-tools-title">
        <div className="flex items-start justify-between gap-4 border-b border-[var(--peer-line)] px-[23px] py-[18px]">
          <div><p className="peer-eyebrow mb-1">Find implementation evidence</p><h2 id="library-tools-title" className="font-display text-[19px] font-semibold tracking-[-0.025em]">Search, categories and filters</h2></div>
          {items[0] ? <Link to={`/usecases/${items[0].company_slug}/${items[0].title_slug}`} className="hidden items-center gap-1 text-xs font-bold text-[var(--peer-blue)] sm:inline-flex">Open selected <ArrowRight className="size-3.5" /></Link> : null}
        </div>
        <div className="grid gap-2.5 border-b border-[var(--peer-line)] bg-[#f7f5ee] px-[22px] py-[18px] lg:grid-cols-[minmax(260px,1fr)_190px_auto]">
          <label className="relative block">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-teal)]" />
            <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} className="h-[42px] w-full border border-[var(--peer-line)] bg-white pl-10 pr-3 text-[13px] outline-none focus:border-[var(--peer-blue)]" placeholder="Search technology, challenge, company or city" aria-label="Search use cases" />
          </label>
          <label className="relative block">
            <Factory className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-[var(--peer-teal)]" />
            <select value={category} onChange={(event) => setCategory(event.target.value)} className="h-[42px] w-full appearance-none border border-[var(--peer-line)] bg-white pl-10 pr-3 text-[13px] outline-none focus:border-[var(--peer-blue)]" aria-label="Filter by category">
              {categories.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:flex">
            {sortOptions.map((option) => (
              <Button key={option.id} variant="outline" onClick={() => setSortBy(option.id)} className={`h-[42px] w-full rounded-none px-3 text-xs lg:w-auto ${sortBy === option.id ? "border-[var(--peer-navy)] bg-[var(--peer-navy)] text-white hover:bg-[#174550] hover:text-white" : "border-[var(--peer-line)] bg-white"}`}>
                <ArrowUpDown className="size-3.5" />{option.label}
              </Button>
            ))}
          </div>
        </div>
        {(category !== "all" || query) ? (
          <div className="flex flex-wrap gap-2 border-b border-[var(--peer-line)] px-[22px] py-3.5">
            {activeCategory && category !== "all" ? <span className="inline-flex min-h-[30px] items-center gap-1.5 border border-[#c8d6d1] bg-[var(--peer-teal-soft)] px-2.5 text-xs font-bold text-[var(--peer-teal)]"><Activity className="size-3.5" />{activeCategory.name}</span> : null}
            {query ? <span className="inline-flex min-h-[30px] items-center gap-1.5 border border-[#c8d6d1] bg-[var(--peer-teal-soft)] px-2.5 text-xs font-bold text-[var(--peer-teal)]"><Search className="size-3.5" />{query}</span> : null}
            <button type="button" onClick={() => { setCategory("all"); setQuery("") }} className="inline-flex min-h-[30px] items-center gap-1.5 border border-[var(--peer-line)] px-2.5 text-xs font-bold text-[var(--peer-muted)]"><X className="size-3.5" />Clear filters</button>
          </div>
        ) : null}
        {visibleCategories.length ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3">
            {visibleCategories.map((item, index) => {
              const Icon = categoryIcons[index] || Factory
              return (
                <button key={item.id} type="button" onClick={() => setCategory(item.id)} className="group grid min-h-32 content-between gap-3 border-b border-[var(--peer-line)] p-[19px] text-left hover:bg-[#f2f5f1] sm:border-r lg:last:border-r-0">
                  <span className="flex items-start justify-between"><span className="grid size-[39px] place-items-center border border-[#c4d7d1] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]"><Icon className="size-[19px]" /></span><span className="text-[11px] font-bold text-[var(--peer-muted)]">{item.count}</span></span>
                  <span><strong className="block text-sm">{item.name}</strong><span className="mt-1 block text-xs leading-5 text-[var(--peer-muted)]">{categoryDescriptions[index]}</span></span>
                </button>
              )
            })}
          </div>
        ) : null}
      </section>

      <div className="grid items-start gap-[22px] xl:grid-cols-[minmax(0,1.56fr)_minmax(292px,0.74fr)]">
        <section className="peer-panel overflow-hidden" aria-labelledby="results-title">
          <div className="flex items-start justify-between gap-4 border-b border-[var(--peer-line)] px-[23px] py-[18px]">
            <div><p className="peer-eyebrow mb-1">Library results</p><h2 id="results-title" className="font-display text-[19px] font-semibold">{total} use cases</h2></div>
            {loading ? <span className="text-xs text-[var(--peer-muted)]">Updating…</span> : <span className="text-xs text-[var(--peer-muted)]">Page {page} of {totalPages}</span>}
          </div>
          {items.length === 0 ? (
            <EmptyState className="border-0 shadow-none" title="No use cases match these filters" description="Broaden the category or search terms to find more implementation examples." actionLabel="Clear filters" onAction={() => { setQuery(""); setCategory("all") }} />
          ) : (
            <ul className="m-0 list-none p-0">
              {items.map((item) => {
                const itemBenefits = displayMetrics(item.results?.benefits)
                return (
                  <li key={item.id} className="grid gap-4 border-b border-[var(--peer-line)] px-[22px] py-5 last:border-b-0 hover:bg-[#f2f5f1] md:grid-cols-[104px_minmax(0,1fr)_auto]">
                    <button type="button" onClick={() => navigate(`/usecases/${item.company_slug}/${item.title_slug}`)} className="grid h-[104px] w-full place-items-center self-start overflow-hidden border border-[#c4d7d1] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)] md:w-[104px]" aria-label={`Open ${item.title}`}>
                      {item.image ? <img src={item.image} alt="" className="h-full w-full object-cover" /> : <Activity className="size-8" />}
                    </button>
                    <div className="min-w-0">
                      <div className="mb-2 flex flex-wrap items-center gap-2 text-[11px] text-[var(--peer-muted)]">
                        <span className="inline-flex min-h-[28px] items-center gap-1.5 border border-[#c8d6d1] bg-[var(--peer-teal-soft)] px-2.5 font-bold text-[var(--peer-teal)]">{item.verified ? <CheckCircle2 className="size-3.5" /> : <Factory className="size-3.5" />}{item.category}</span>
                        {item.industry ? <span>{item.industry}</span> : null}<span>{item.company}</span>
                      </div>
                      <Link to={`/usecases/${item.company_slug}/${item.title_slug}`} className="font-display text-[17px] font-bold leading-[1.3] tracking-[-0.02em] hover:text-[var(--peer-blue)]">{item.title}</Link>
                      <p className="mt-1.5 line-clamp-2 text-[13px] leading-5 text-[var(--peer-muted)]">{item.description || "Open this implementation to review its challenge, approach, measured outcomes, and lessons learned."}</p>
                      <div className="mt-3 flex flex-wrap items-center gap-1 text-xs text-[var(--peer-muted)]">
                        <span className="inline-flex items-center gap-1 px-2"><Eye className="size-3.5" />{item.views}</span>
                        <button type="button" onClick={() => void toggleLike(item)} className={`inline-flex min-h-8 items-center gap-1 px-2 font-semibold hover:text-[var(--peer-teal)] ${liked.has(item.id) ? "text-[var(--peer-teal)]" : ""}`} aria-label="Like use case"><ThumbsUp className={`size-3.5 ${liked.has(item.id) ? "fill-current" : ""}`} />{item.likes}</button>
                        <button type="button" onClick={() => void toggleBookmark(item)} className={`inline-flex min-h-8 items-center gap-1 px-2 font-semibold hover:text-[var(--peer-teal)] ${bookmarked.has(item.id) ? "text-[var(--peer-teal)]" : ""}`} aria-label="Save use case"><Bookmark className={`size-3.5 ${bookmarked.has(item.id) ? "fill-current" : ""}`} />{item.saves}</button>
                      </div>
                    </div>
                    {itemBenefits.length ? (
                      <div className="grid grid-cols-2 self-center border border-[var(--peer-line)] bg-[var(--peer-line)]">
                        {itemBenefits.map((benefit) => {
                          const part = benefitParts(benefit)
                          return <span key={benefit} className="grid min-h-[70px] min-w-[92px] max-w-[120px] content-center justify-items-center bg-[#f5f4ef] px-3 text-center"><strong className="font-display text-[15px]">{part.headline}</strong><span className="mt-1 line-clamp-2 text-[10px] leading-4 text-[var(--peer-muted)]">{part.label}</span></span>
                        })}
                      </div>
                    ) : null}
                  </li>
                )
              })}
            </ul>
          )}
          {totalPages > 1 ? (
            <div className="flex items-center justify-center gap-3 border-t border-[var(--peer-line)] p-4">
              <Button variant="outline" className="rounded-none bg-white" disabled={page === 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Previous</Button>
              <span className="text-xs text-[var(--peer-muted)]">Page {page} of {totalPages}</span>
              <Button variant="outline" className="rounded-none bg-white" disabled={page === totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))}>Next</Button>
            </div>
          ) : null}
        </section>

        <aside className="grid gap-[22px]">
          <section className="peer-panel overflow-hidden">
            <div className="border-b border-[var(--peer-line)] px-5 py-[18px]"><p className="peer-eyebrow mb-1">Featured evidence</p><h2 className="font-display text-[19px] font-semibold">High-signal cases</h2></div>
            <ul className="m-0 list-none p-0">
              {(featuredItems.length ? featuredItems : items.slice(0, 3)).map((item) => {
                const metrics = displayMetrics(item.results?.benefits)
                const summary = metrics.length ? metrics.join(" · ") : compactSummary(item.description)
                return <li key={item.id} className="border-b border-[var(--peer-line)] px-5 py-3.5 last:border-b-0"><Link to={`/usecases/${item.company_slug}/${item.title_slug}`} className="text-[13px] font-bold hover:text-[var(--peer-blue)]">{item.title}</Link><span className="mt-1 block text-[11px] leading-4 text-[var(--peer-muted)]">{summary}</span></li>
              })}
            </ul>
          </section>
          <section className="peer-panel overflow-hidden">
            <div className="border-b border-[var(--peer-line)] px-5 py-[18px]"><p className="peer-eyebrow mb-1">Network evidence</p><h2 className="font-display text-[19px] font-semibold">Library at a glance</h2></div>
            <dl className="m-0">
              <div className="flex justify-between border-b border-[var(--peer-line)] px-5 py-3.5 text-xs"><dt className="text-[var(--peer-muted)]">Published cases</dt><dd className="font-display font-bold">{stats?.totalUseCases ?? total}</dd></div>
              <div className="flex justify-between border-b border-[var(--peer-line)] px-5 py-3.5 text-xs"><dt className="text-[var(--peer-muted)]">Contributing companies</dt><dd className="font-display font-bold">{stats?.contributingCompanies ?? "—"}</dd></div>
              <div className="flex justify-between px-5 py-3.5 text-xs"><dt className="text-[var(--peer-muted)]">Featured stories</dt><dd className="font-display font-bold">{stats?.successStories ?? "—"}</dd></div>
            </dl>
            <Link to="/submit" className="grid grid-cols-[1fr_auto] items-center gap-3 border-t border-[var(--peer-line)] bg-[#f1f2ed] px-5 py-4"><span><strong className="block text-[13px]">Start submission</strong><span className="text-[11px] text-[var(--peer-muted)]">Three simple steps · about 5–10 minutes</span></span><span className="font-display text-[22px] font-bold text-[var(--peer-teal)]">3</span></Link>
          </section>
        </aside>
      </div>
    </main>
  )
}

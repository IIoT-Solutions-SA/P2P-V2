import { useEffect, useMemo, useState } from "react"
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom"
import {
  Bell,
  ChevronRight,
  LogOut,
  Menu,
  Search,
  Settings,
  User,
  X,
} from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { Avatar } from "@/components/ui/Avatar"
import { EditProfilePanel } from "@/components/EditProfilePanel"
import { cn } from "@/lib/utils"
import { BrandMark } from "@/components/layout/BrandMark"
import { organizationNavItems, workspaceNavItems } from "@/components/layout/navigation"
import type { AppNavItem } from "@/components/layout/navigation"
import { formatOrganizationName } from "@/lib/formatters"
import { dashboardApi, type DashboardActivity } from "@/lib/api/dashboard"

const isPathActive = (pathname: string, itemPath: string) => pathname === itemPath || pathname.startsWith(`${itemPath}/`)

function SidebarLink({ item, compact = false, onClick }: { item: AppNavItem; compact?: boolean; onClick?: () => void }) {
  const location = useLocation()
  const active = isPathActive(location.pathname, item.path)
  const Icon = item.icon

  return (
    <Link
      to={item.path}
      reloadDocument={item.path === "/organization" || item.path === "/usecases"}
      onClick={onClick}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex min-h-11 items-center gap-3 border-l-2 border-transparent px-3 text-sm font-medium text-[#b8cbca] transition hover:bg-white/[0.055] hover:text-white",
        active && "border-[#76c5bd] bg-[#75c3ba1c] text-white",
        compact && "justify-center px-0"
      )}
      title={compact ? item.label : undefined}
    >
      <Icon className="size-[18px] shrink-0" aria-hidden="true" />
      {!compact ? <span className="truncate">{item.label}</span> : null}
    </Link>
  )
}

function NavGroup({
  label,
  items,
  compact = false,
  onItemClick,
}: {
  label: string
  items: AppNavItem[]
  compact?: boolean
  onItemClick?: () => void
}) {
  if (items.length === 0) return null

  return (
    <div className="mb-6">
      {!compact ? <p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.13em] text-[#78999c]">{label}</p> : null}
      <nav className="grid gap-1" aria-label={label}>
        {items.map((item) => (
          <SidebarLink key={item.path} item={item} compact={compact} onClick={onItemClick} />
        ))}
      </nav>
    </div>
  )
}

function UserRail({
  compact = false,
  onEditProfile,
  onLogout,
}: {
  compact?: boolean
  onEditProfile: () => void
  onLogout: () => void
}) {
  const { user } = useAuth()
  const name = `${user?.firstName || ""} ${user?.lastName || ""}`.trim() || user?.email || "PeerLink user"

  return (
    <div className={cn("border-t border-white/15 pt-4", compact && "grid justify-center")}>
      <button
        type="button"
        onClick={onEditProfile}
        className={cn("grid w-full grid-cols-[36px_1fr_auto] items-center gap-3 px-3 py-2 text-left hover:bg-white/[0.055]", compact && "flex w-11 justify-center px-0")}
        aria-label="Open profile settings"
      >
        <Avatar src={user?.profilePictureUrl} name={name} size="sm" />
        {!compact ? (
          <>
            <span className="min-w-0">
              <span className="block truncate text-xs font-semibold text-white">{name}</span>
              <span className="block truncate text-[10px] text-[#91aaac]">{user?.role === "admin" ? "Administrator" : "Member"}</span>
            </span>
            <Settings className="size-4 text-[#aec1c2]" aria-hidden="true" />
          </>
        ) : null}
      </button>
      {!compact ? (
        <button
          type="button"
          onClick={onLogout}
          className="mt-1 flex w-full items-center gap-3 px-3 py-2 text-sm font-medium text-[#b8cbca] hover:bg-white/[0.055] hover:text-white"
        >
          <LogOut className="size-4" aria-hidden="true" />
          Log out
        </button>
      ) : null}
    </div>
  )
}

const activityLabel = (activity: DashboardActivity) =>
  activity.target_title || activity.content || activity.description || "PeerLink network update"

function WorkspaceTopbar({ onMobileMenu }: { onMobileMenu: () => void }) {
  const location = useLocation()
  const navigate = useNavigate()
  const { organization } = useAuth()
  const [searchOpen, setSearchOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [query, setQuery] = useState("")
  const [activities, setActivities] = useState<DashboardActivity[]>([])
  const [notificationsSeen, setNotificationsSeen] = useState(false)
  const currentItem = [...workspaceNavItems, ...organizationNavItems].find((item) => isPathActive(location.pathname, item.path))
  const currentLabel = location.pathname === "/submit"
    ? "New submission"
    : currentItem?.label === "Organization" ? formatOrganizationName(organization?.name) : currentItem?.label || "Workspace"
  const searchItems = useMemo(() => [
    ...workspaceNavItems,
    ...organizationNavItems.map((item) => ({ ...item, label: formatOrganizationName(organization?.name, item.label) })),
    { label: "Submit a use case", path: "/submit", icon: Search },
  ], [organization?.name])
  const visibleSearchItems = searchItems.filter((item) => item.label.toLowerCase().includes(query.trim().toLowerCase()))

  useEffect(() => {
    void dashboardApi.activities()
      .then((result) => setActivities((result.activities || []).slice(0, 5)))
      .catch(() => setActivities([]))
  }, [])

  const openNotifications = () => {
    setNotificationsOpen((value) => !value)
    setSearchOpen(false)
    setNotificationsSeen(true)
  }

  return (
    <header className="sticky top-0 z-20 flex h-[calc(var(--peer-topbar-height)+env(safe-area-inset-top))] items-center justify-between gap-4 border-b border-[var(--peer-line)] bg-[rgba(243,240,232,0.94)] px-4 pt-[env(safe-area-inset-top)] backdrop-blur md:px-8 xl:px-14">
      <div className="flex min-w-0 items-center gap-3">
        <button type="button" onClick={onMobileMenu} className="grid size-11 place-items-center border border-[var(--peer-line)] bg-white text-[var(--peer-ink)] md:hidden" aria-label="Open navigation menu">
          <Menu className="size-5" />
        </button>
        <div className="hidden items-center gap-2 text-sm text-[var(--peer-muted)] sm:flex">
          <span>PeerLink</span><ChevronRight className="size-4" aria-hidden="true" /><strong className="truncate font-semibold text-[var(--peer-ink)]">{currentLabel}</strong>
        </div>
        <h1 className="font-display truncate text-lg font-semibold sm:hidden">{currentLabel}</h1>
      </div>
      <div className="relative flex items-center gap-2">
        <div className="mr-1 hidden items-center gap-2 text-xs text-[var(--peer-muted)] md:flex"><span className="size-2 rounded-full bg-[var(--peer-success)] shadow-[0_0_0_3px_rgba(22,133,109,0.12)]" />Network active</div>
        <button type="button" onClick={() => { setSearchOpen((value) => !value); setNotificationsOpen(false) }} className="grid size-10 place-items-center border border-[var(--peer-line)]" aria-label="Search workspace" aria-expanded={searchOpen}>
          <Search className="size-4" aria-hidden="true" />
        </button>
        <button type="button" onClick={openNotifications} className="relative grid size-10 place-items-center border border-[var(--peer-line)]" aria-label="Notifications" aria-expanded={notificationsOpen}>
          <Bell className="size-4" aria-hidden="true" />
          {!notificationsSeen && activities.length > 0 ? <span className="absolute right-2 top-2 size-2 rounded-full bg-[var(--peer-blue)]" /> : null}
        </button>

        {searchOpen ? (
          <section className="absolute right-0 top-12 z-50 w-[min(88vw,420px)] border border-[var(--peer-line)] bg-white shadow-[var(--peer-shadow)]" aria-label="Workspace search panel">
            <div className="border-b border-[var(--peer-line)] p-4">
              <p className="peer-eyebrow mb-2">Workspace search</p>
              <label className="flex items-center gap-2 border border-[var(--peer-line)] bg-[#f7f6f1] px-3"><Search className="size-4 text-[var(--peer-muted)]" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Find a workspace area" className="h-11 min-w-0 flex-1 bg-transparent text-sm outline-none" /></label>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {visibleSearchItems.map((item) => <button key={item.path} type="button" onClick={() => { if (item.path === "/organization" || item.path === "/usecases") window.location.assign(item.path); else navigate(item.path); setSearchOpen(false); setQuery("") }} className="flex w-full items-center justify-between border-b border-[var(--peer-line)] px-3 py-3 text-left text-sm font-semibold last:border-b-0 hover:bg-[#f2f5f1]"><span>{item.label}</span><ChevronRight className="size-4 text-[var(--peer-muted)]" /></button>)}
              {visibleSearchItems.length === 0 ? <p className="px-3 py-8 text-center text-sm text-[var(--peer-muted)]">No workspace area matches “{query}”.</p> : null}
            </div>
          </section>
        ) : null}

        {notificationsOpen ? (
          <section className="absolute right-0 top-12 z-50 w-[min(88vw,430px)] border border-[var(--peer-line)] bg-white shadow-[var(--peer-shadow)]" aria-label="Notifications panel">
            <div className="border-b border-[var(--peer-line)] p-4"><p className="peer-eyebrow">Network activity</p><h2 className="font-display text-xl font-semibold">Notifications</h2><p className="mt-1 text-xs text-[var(--peer-muted)]">Recent verified activity across PeerLink.</p></div>
            <div className="max-h-[420px] overflow-y-auto">
              {activities.length > 0 ? activities.map((activity, index) => <div key={`${activityLabel(activity)}-${index}`} className="border-b border-[var(--peer-line)] p-4 last:border-b-0"><strong className="block text-sm">{activityLabel(activity)}</strong><p className="mt-1 text-xs text-[var(--peer-muted)]">{activity.user || "PeerLink member"} · {activity.action || activity.activity_type || "shared an update"}</p><p className="mt-1 text-[11px] text-[#858e90]">{activity.time || (activity.created_at ? new Date(activity.created_at).toLocaleString() : "Recently")}</p></div>) : <div className="p-8 text-center"><strong className="text-sm">You are up to date</strong><p className="mt-1 text-xs text-[var(--peer-muted)]">New discussions and implementation updates will appear here.</p></div>}
            </div>
            <button type="button" onClick={() => { navigate("/dashboard"); setNotificationsOpen(false) }} className="w-full border-t border-[var(--peer-line)] px-4 py-3 text-sm font-bold text-[var(--peer-blue)] hover:bg-[#f2f5f1]">View all network activity</button>
          </section>
        ) : null}
      </div>
    </header>
  )
}

export function AuthenticatedLayout() {
  const { organization, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [showEditProfile, setShowEditProfile] = useState(false)
  const [editProfileTab, setEditProfileTab] = useState<"profile" | "account">("profile")

  const visibleOrganizationItems = organizationNavItems.map((item) => ({ ...item, label: formatOrganizationName(organization?.name, item.label) }))

  const handleLogout = async () => {
    await logout()
    navigate("/home")
  }

  const openProfile = (tab: "profile" | "account" = "profile") => {
    setEditProfileTab(tab)
    setShowEditProfile(true)
    setMobileOpen(false)
  }

  return (
    <div className="peer-workspace">
      <a className="fixed left-4 top-[-80px] z-[100] border border-[var(--peer-blue)] bg-white px-4 py-2 text-[var(--peer-navy)] focus:top-3" href="#workspace-content">
        Skip to content
      </a>

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[var(--peer-rail-width)] flex-col border-r border-white/15 bg-[var(--peer-navy)] text-[#ecf3f1] lg:flex">
        <div className="flex h-[var(--peer-topbar-height)] items-center border-b border-white/15 px-6">
          <BrandMark />
        </div>
        <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-4 py-6">
          <NavGroup label="Workspace" items={workspaceNavItems} />
          <NavGroup label="Organization" items={visibleOrganizationItems} />
          <div className="flex-1" />
          <button
            type="button"
            onClick={() => openProfile("account")}
            className="mb-2 flex items-center gap-3 px-3 py-2 text-sm font-medium text-[#b8cbca] hover:bg-white/[0.055] hover:text-white"
          >
            <User className="size-4" aria-hidden="true" />
            Password & security
          </button>
          <UserRail onEditProfile={() => openProfile("profile")} onLogout={() => void handleLogout()} />
        </div>
      </aside>

      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[var(--peer-rail-compact)] flex-col border-r border-white/15 bg-[var(--peer-navy)] text-[#ecf3f1] md:flex lg:hidden">
        <div className="grid h-[var(--peer-topbar-height)] place-items-center border-b border-white/15">
          <BrandMark compact />
        </div>
        <div className="flex min-h-0 flex-1 flex-col overflow-y-auto px-3 py-6">
          <NavGroup label="Workspace" items={workspaceNavItems} compact />
          <NavGroup label="Organization" items={visibleOrganizationItems} compact />
          <div className="flex-1" />
          <UserRail compact onEditProfile={() => openProfile("profile")} onLogout={() => void handleLogout()} />
        </div>
      </aside>

      {mobileOpen ? (
        <div className="fixed inset-0 z-40 bg-black/45 md:hidden" onClick={() => setMobileOpen(false)}>
          <div className="absolute inset-y-0 left-0 w-[min(88vw,340px)] bg-[var(--peer-navy)] text-[#ecf3f1]" onClick={(event) => event.stopPropagation()}>
            <div className="flex h-[var(--peer-topbar-height)] items-center justify-between border-b border-white/15 px-5">
              <BrandMark />
              <button type="button" onClick={() => setMobileOpen(false)} className="grid size-10 place-items-center" aria-label="Close navigation menu">
                <X className="size-5" />
              </button>
            </div>
            <div className="flex h-[calc(100%-var(--peer-topbar-height))] flex-col overflow-y-auto px-4 pb-[calc(1.5rem+env(safe-area-inset-bottom))] pt-6">
              <NavGroup label="Workspace" items={workspaceNavItems} onItemClick={() => setMobileOpen(false)} />
              <NavGroup label="Organization" items={visibleOrganizationItems} onItemClick={() => setMobileOpen(false)} />
              <div className="flex-1" />
              <UserRail onEditProfile={() => openProfile("profile")} onLogout={() => void handleLogout()} />
            </div>
          </div>
        </div>
      ) : null}

      <div className="min-h-[100dvh] md:ml-[var(--peer-rail-compact)] lg:ml-[var(--peer-rail-width)]">
        <WorkspaceTopbar onMobileMenu={() => setMobileOpen(true)} />
        <main id="workspace-content" className="min-h-[calc(100vh-var(--peer-topbar-height))]">
          <Outlet />
        </main>
      </div>

      <EditProfilePanel
        isOpen={showEditProfile}
        onClose={() => setShowEditProfile(false)}
        onSave={() => setShowEditProfile(false)}
        initialTab={editProfileTab}
      />
    </div>
  )
}

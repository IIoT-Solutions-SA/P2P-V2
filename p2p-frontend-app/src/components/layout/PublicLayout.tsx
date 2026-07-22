import { Outlet, useNavigate } from "react-router-dom"
import { BookOpen, Factory, LayoutDashboard, MapPinned, Network, UserPlus } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"
import { BrandMark } from "@/components/layout/BrandMark"

const publicSections = [
  { label: "Overview", href: "#overview", icon: LayoutDashboard },
  { label: "Network", href: "#network", icon: Network },
  { label: "Saudi Map", href: "#saudi-map", icon: MapPinned },
  { label: "Use Cases", href: "#featured-use-cases", icon: BookOpen },
  { label: "Join", href: "#join-network", icon: UserPlus },
]

export function PublicLayout() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-[var(--peer-paper)]">
      <aside className="fixed inset-y-0 left-0 z-50 hidden w-[280px] flex-col border-r border-white/10 bg-[var(--peer-navy)] text-white lg:flex">
        <div className="border-b border-white/10 px-7 py-7">
          <BrandMark />
          <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.22em] text-[#76c5bd]">Network workspace</p>
        </div>

        <nav className="flex-1 px-4 py-7" aria-label="Public homepage sections">
          <p className="px-3 text-[10px] font-bold uppercase tracking-[0.22em] text-[#7fa0a3]">Explore</p>
          <div className="mt-3 space-y-1">
            {publicSections.map((item, index) => (
              <a
                key={item.label}
                href={item.href}
                className={`flex items-center gap-3 border-l-2 px-4 py-3 text-sm transition ${index === 0 ? "border-[#76c5bd] bg-white/8 text-white" : "border-transparent text-[#c7d8d7] hover:border-[#76c5bd]/60 hover:bg-white/5 hover:text-white"}`}
              >
                <item.icon className="size-4" />
                {item.label}
              </a>
            ))}
          </div>
        </nav>

        <div className="m-5 border border-white/12 bg-white/5 p-4">
          <div className="flex items-center gap-2 text-xs font-bold text-white"><Factory className="size-4 text-[#76c5bd]" />Public preview mode</div>
          <p className="mt-2 text-xs leading-5 text-[#9cb4b5]">Visitors can inspect city markers and uploaded use cases before signing in.</p>
          <div className="mt-4 grid gap-2">
            <Button onClick={() => navigate(isAuthenticated ? "/dashboard" : "/signup")} className="rounded-none bg-[var(--peer-teal)] text-white hover:bg-[#0b4f4d]">
              {isAuthenticated ? "Open workspace" : "Join network"}
            </Button>
            {!isAuthenticated ? <Button onClick={() => navigate("/login")} variant="outline" className="rounded-none border-white/20 bg-transparent text-white hover:bg-white/10 hover:text-white">Sign in</Button> : null}
          </div>
        </div>
      </aside>

      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[rgba(11,47,57,0.96)] px-4 py-3 text-white backdrop-blur lg:hidden">
        <div className="flex items-center justify-between gap-3">
          <BrandMark />
          <Button className="bg-[var(--peer-teal)] text-white hover:bg-[#0b4f4d]" onClick={() => navigate(isAuthenticated ? "/dashboard" : "/signup")}>{isAuthenticated ? "Workspace" : "Join"}</Button>
        </div>
      </header>

      <main className="pt-16 lg:pl-[280px] lg:pt-0">
        <Outlet />
      </main>
    </div>
  )
}

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-[var(--peer-paper)]">
      <Outlet />
    </div>
  )
}

import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import {
  BadgeCheck,
  CheckCircle2,
  CircleHelp,
  Headphones,
  LockKeyhole,
  Mail,
  ShieldCheck,
  TicketCheck,
  UsersRound,
  type LucideIcon,
} from "lucide-react"
import authBrandLogo from "@/assets/peerlink-logo-dark-sidebar.svg"

type RailStep = {
  label: string
  detail: string
}

type ContextItem = {
  icon: LucideIcon
  title: string
  body: string
  tone?: "teal" | "blue" | "amber" | "success" | "danger"
}

const toneClass = {
  teal: "bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]",
  blue: "bg-[#e6eefb] text-[#17549a]",
  amber: "bg-[#f3e8d9] text-[var(--peer-amber)]",
  success: "bg-[#e0eee9] text-[var(--peer-success)]",
  danger: "bg-[#f8e8e5] text-[var(--peer-danger)]",
}

export function AuthScaffold({
  eyebrow,
  title,
  copy,
  steps,
  activeStep = 1,
  children,
  contextTitle,
  contextItems,
  wide = false,
}: {
  eyebrow: string
  title?: string
  copy?: string
  steps?: RailStep[]
  activeStep?: number
  children: ReactNode
  contextTitle: string
  contextItems: ContextItem[]
  wide?: boolean
}) {
  return (
    <div className="grid min-h-screen grid-cols-1 bg-[var(--peer-paper)] text-[var(--peer-ink)] lg:grid-cols-[320px_minmax(0,1fr)]">
      <aside className="flex flex-col bg-[linear-gradient(160deg,var(--peer-navy)_0%,#06252d_100%)] px-6 py-6 text-[#eaf3f1] lg:min-h-screen lg:px-9 lg:py-8">
        <Link
          to="/home"
          className="block w-full max-w-[238px] pb-7 lg:pb-9"
          aria-label="PeerLink public homepage"
        >
          <img src={authBrandLogo} alt="Saudi Arabia Centre for the Fourth Industrial Revolution — PeerLink for SMEs" className="h-auto w-full" />
        </Link>
        <div className="flex flex-1 flex-col">
          <p className="peer-eyebrow mb-4 text-[#8eb0af]">{eyebrow}</p>
          {steps ? (
            <ol className="grid grid-cols-3 gap-2 lg:grid-cols-1 lg:gap-6">
              {steps.map((step, index) => {
                const isActive = index + 1 === activeStep
                return (
                  <li key={step.label} className="grid min-w-0 grid-cols-[28px_minmax(0,1fr)] items-start gap-2 lg:grid-cols-[38px_minmax(0,1fr)] lg:gap-4">
                    <span className={`grid size-7 place-items-center rounded-full border-2 text-xs font-bold lg:size-9 ${isActive ? "border-[#27c8ae] text-white shadow-[0_0_0_4px_rgba(39,200,174,.08)]" : "border-[#6c9292] text-[#d7e5e3]"}`}>
                      {index + 1}
                    </span>
                    <span className="min-w-0">
                      <strong className="block truncate text-[10px] text-white lg:text-sm">{step.label}</strong>
                      <span className="hidden text-xs text-[#9fb8b7] lg:block">{step.detail}</span>
                    </span>
                  </li>
                )
              })}
            </ol>
          ) : (
            <>
              <h2 className="font-display max-w-[250px] text-2xl font-semibold leading-tight text-white">{title}</h2>
              <p className="mt-3 max-w-[260px] text-sm text-[#a9bfbe]">{copy}</p>
              <ul className="mt-8 grid gap-5">
                {[
                  { icon: BadgeCheck, title: "Verified manufacturers", body: "Connect with trusted manufacturers and partners." },
                  { icon: LockKeyhole, title: "Secure access", body: "Device-aware verification protects organization data." },
                  { icon: UsersRound, title: "Knowledge exchange", body: "Share expertise and solve real manufacturing challenges." },
                ].map((item) => (
                  <li key={item.title} className="grid grid-cols-[43px_minmax(0,1fr)] gap-3">
                    <span className="grid size-11 place-items-center rounded-lg border border-[#bce2dc]/30 bg-white/5 text-[#bce2dc]">
                      <item.icon className="size-5" />
                    </span>
                    <span>
                      <strong className="block text-sm text-white">{item.title}</strong>
                      <span className="mt-1 block text-xs leading-relaxed text-[#a9bfbe]">{item.body}</span>
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
        <footer className="hidden border-t border-white/15 pt-5 text-xs text-[#9db5b4] lg:block">
          <p className="mb-2 flex items-center gap-2">
            <Headphones className="size-4" />
            <span>Need help? <Link className="text-[#dce9e6]" to="/home">Visit support</Link></span>
          </p>
          <p>Built for manufacturing teams</p>
        </footer>
      </aside>

      <div className="min-w-0">
        <header className="hidden min-h-16 items-center justify-end gap-6 border-b border-[var(--peer-line)]/80 px-8 text-sm font-semibold text-[var(--peer-muted)] md:flex">
          <Link className="inline-flex items-center gap-2 text-[var(--peer-ink)]" to="/home">Public homepage</Link>
          <Link className="inline-flex items-center gap-2 text-[var(--peer-ink)]" to="/home"><CircleHelp className="size-4" />Need help?</Link>
        </header>
        <section className="grid min-h-[calc(100vh-8rem)] place-items-center px-3 py-6 sm:px-5 lg:px-12 lg:py-16">
          <div className={`grid w-full items-center gap-7 ${wide ? "max-w-6xl lg:grid-cols-[minmax(500px,1.3fr)_minmax(310px,.75fr)]" : "max-w-5xl lg:grid-cols-[minmax(430px,1.22fr)_minmax(310px,.82fr)]"}`}>
            {children}
            <AuthContextPanel title={contextTitle} items={contextItems} />
          </div>
        </section>
      </div>
    </div>
  )
}

export function AuthCard({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <main className={`peer-panel rounded-[7px] p-6 sm:p-8 lg:p-12 ${className}`}>
      {children}
    </main>
  )
}

export function AuthContextPanel({ title, items }: { title: string; items: ContextItem[] }) {
  return (
    <aside className="peer-panel rounded-[7px] p-6 sm:p-8">
      <h2 className="font-display mb-5 text-xl font-bold text-[var(--peer-ink)]">{title}</h2>
      <ul className="grid">
        {items.map((item) => (
          <li key={item.title} className="grid grid-cols-[48px_minmax(0,1fr)] gap-4 border-b border-[var(--peer-line)] py-4 first:pt-0 last:border-b-0 last:pb-0">
            <span className={`grid size-12 place-items-center rounded-lg ${toneClass[item.tone ?? "teal"]}`}>
              <item.icon className="size-6" />
            </span>
            <span>
              <strong className="block text-sm text-[var(--peer-ink)]">{item.title}</strong>
              <span className="mt-1 block text-xs leading-relaxed text-[var(--peer-muted)]">{item.body}</span>
            </span>
          </li>
        ))}
      </ul>
      <div className="mt-5 flex items-center gap-2 rounded-[5px] border border-[var(--peer-line)] p-3 text-xs text-[var(--peer-muted)]">
        <ShieldCheck className="size-4 text-[var(--peer-teal)]" />
        <span>Your data is protected with industry-standard security.</span>
      </div>
    </aside>
  )
}

export function AuthHeading({ title, subtitle }: { title: string; subtitle: ReactNode }) {
  return (
    <div className="mb-7">
      <h1 className="font-display text-3xl font-bold leading-tight text-[#07161d] sm:text-4xl">{title}</h1>
      <p className="mt-2 text-sm leading-relaxed text-[var(--peer-muted)]">{subtitle}</p>
    </div>
  )
}

export function AuthAlert({
  tone = "info",
  title,
  children,
}: {
  tone?: "info" | "error" | "success" | "warning"
  title?: string
  children: ReactNode
}) {
  const styles = {
    info: "border-[#c7d8f3] bg-[#e6eefb] text-[#174c89]",
    error: "border-[#e5bbb6] bg-[#f8e8e5] text-[#812e2c]",
    success: "border-[#b9d9cf] bg-[#e0eee9] text-[#0e6554]",
    warning: "border-[#e5ceb0] bg-[#f3e8d9] text-[#815019]",
  }
  const Icon = tone === "success" ? CheckCircle2 : tone === "info" ? TicketCheck : Mail
  return (
    <div className={`mb-5 grid grid-cols-[20px_minmax(0,1fr)] gap-3 rounded-[5px] border p-3 text-sm ${styles[tone]}`} role={tone === "error" ? "alert" : "status"}>
      <Icon className="mt-0.5 size-5" />
      <span>
        {title ? <strong className="block">{title}</strong> : null}
        <span className="block text-xs leading-relaxed">{children}</span>
      </span>
    </div>
  )
}

export function FieldError({ message }: { message?: string }) {
  if (!message) return null
  return <p className="mt-1 text-xs font-medium text-[var(--peer-danger)]">{message}</p>
}

export function PasswordRequirements({ password }: { password: string }) {
  const checks = [
    { label: "8+ characters", ok: password.length >= 8 },
    { label: "Lowercase letter", ok: /[a-z]/.test(password) },
    { label: "Number", ok: /[0-9]/.test(password) },
    { label: "Symbol recommended", ok: /[^A-Za-z0-9]/.test(password) },
  ]
  const strength = checks.filter((check) => check.ok).length
  return (
    <div className="mt-3">
      <div className="grid grid-cols-4 gap-1">
        {checks.map((check, index) => (
          <span key={check.label} className={`h-1 rounded-full ${index < strength ? (strength < 2 ? "bg-[var(--peer-danger)]" : strength < 4 ? "bg-[var(--peer-amber)]" : "bg-[var(--peer-success)]") : "bg-[var(--peer-line)]"}`} />
        ))}
      </div>
      <ul className="mt-2 grid grid-cols-1 gap-1 text-xs text-[var(--peer-muted)] sm:grid-cols-2">
        {checks.map((check) => (
          <li key={check.label} className={check.ok ? "text-[var(--peer-success)]" : ""}>{check.ok ? "Met:" : "Needs:"} {check.label}</li>
        ))}
      </ul>
    </div>
  )
}

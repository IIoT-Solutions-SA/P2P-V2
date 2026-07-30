import type { ReactNode } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowRight, BarChart3, BookOpen, CheckCircle2, Cog, Factory, MapPin, User, Users, Wrench } from "lucide-react"
import { Button } from "@/components/ui/button"
import InteractiveMap from "@/components/InteractiveMap"
import { SaudiRiyalCurrency } from "@/components/SaudiRiyal"
import { useAuth } from "@/contexts/AuthContext"

const stats = [
  { value: "1,200+", label: "Connected Factories" },
  { value: "89", label: "Proven Use Cases" },
  { value: <SaudiRiyalCurrency amount="45M+" />, label: "Cost Savings Achieved" },
  { value: "67%", label: "Avg. Efficiency Gain" },
]

const features = [
  { icon: BookOpen, title: "Browse use cases", body: "Explore real factory implementations with proven results across automation, quality, maintenance, and energy." },
  { icon: Users, title: "Factory network", body: "Connect with manufacturing peers across Saudi Arabia and collaborate around shared operational challenges." },
  { icon: BarChart3, title: "Performance tracking", body: "Monitor efficiency gains, cost savings, and operational improvements as implementation knowledge grows." },
]

const featuredCases = [
  {
    icon: Cog,
    category: "Factory Automation",
    title: "AI Quality Inspection Reduces Defects by 85%",
    body: "Advanced Manufacturing Co. implemented computer vision for automated quality control, achieving significant defect reduction.",
    primary: "85%",
    primaryLabel: "Defect Reduction",
    secondary: <SaudiRiyalCurrency amount="2.3M" />,
    secondaryLabel: "Annual Savings",
    path: "/usecases/advanced-electronics-co/ai-quality-inspection-system",
  },
  {
    icon: Wrench,
    category: "Predictive Maintenance",
    title: "IoT Sensors Cut Downtime by 60%",
    body: "Gulf Plastics Industries deployed IoT-based predictive maintenance, preventing equipment failures before they occur.",
    primary: "60%",
    primaryLabel: "Downtime Reduction",
    secondary: <SaudiRiyalCurrency amount="1.8M" />,
    secondaryLabel: "Annual Savings",
    path: "/usecases/gulf-plastics-industries/predictive-maintenance-iot-system",
  },
]

const stories = [
  { icon: Cog, title: "Production Optimization", desc: "Automated production line monitoring increased output efficiency across multiple facilities.", metric: "45% efficiency gain" },
  { icon: CheckCircle2, title: "Quality Improvements", desc: "Smart quality control systems reduced defects and improved product standards.", metric: "78% defect reduction" },
  { icon: BarChart3, title: "Cost Savings", desc: "Energy management and predictive maintenance programs delivered operational savings.", metric: <><SaudiRiyalCurrency amount="3.2M" className="text-white" /> saved annually</> },
]

export default function LandingPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated } = useAuth()

  return (
    <div className="bg-[var(--peer-paper)] text-[var(--peer-ink)]">
      <section id="overview" className="relative grid min-h-screen scroll-mt-16 items-end overflow-hidden bg-[var(--peer-navy)] text-white">
        <video autoPlay muted loop playsInline className="absolute inset-0 size-full object-cover opacity-70">
          <source src="/Video_Redo_Realistic_Technology.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(11,47,57,.9)_0%,rgba(11,47,57,.58)_45%,rgba(11,47,57,.22)_100%),linear-gradient(180deg,rgba(11,47,57,.14)_0%,rgba(11,47,57,.88)_100%)]" />
        <div className="relative z-10 mx-auto w-full max-w-7xl px-4 pb-10 pt-24 sm:px-6 lg:px-8 lg:pb-14">
          <p className="peer-eyebrow mb-5 inline-flex items-center gap-3 text-[#cde3de] before:h-px before:w-8 before:bg-[#76c5bd]">Saudi manufacturing knowledge network</p>
          <h1 className="font-display max-w-4xl text-5xl font-bold leading-[0.98] text-white sm:text-6xl lg:text-7xl">
            Accelerate factory transformation through verified peer knowledge.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-white/85 sm:text-xl">
            Join Saudi Arabia's premier peer-to-peer platform where manufacturing executives share proven strategies and explore real implementation case studies.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button onClick={() => navigate("/usecases")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] px-6 text-white hover:bg-[#0f5ccc]">
              Explore success stories<ArrowRight className="size-4" />
            </Button>
            <Button onClick={() => window.location.assign("/forum")} variant="outline" className="h-12 rounded-[5px] border-white/35 bg-white/5 px-6 text-white hover:bg-white/10 hover:text-white">
              Join discussions
            </Button>
          </div>
          <div className="mt-12 grid gap-3 border-t border-white/20 pt-5 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="border-l border-[#76c5bd]/40 pl-4">
                <div className="font-display text-3xl font-bold text-white">{stat.value}</div>
                <div className="mt-1 text-sm text-[#c7d8d7]">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="network" className="scroll-mt-16 border-y border-[var(--peer-line)] bg-[var(--peer-surface)]">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
          <div>
            <p className="peer-eyebrow">Network workspace</p>
            <h2 className="font-display mt-3 text-4xl font-bold leading-tight text-[#07161d]">Built around the decisions manufacturers make every week.</h2>
            <p className="mt-4 text-[var(--peer-muted)]">
              PeerLink organizes knowledge, collaborators, case studies, and discussion around verified manufacturing work instead of a generic content feed.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.title} className="border-l border-[var(--peer-line)] pl-5">
                <span className="grid size-11 place-items-center rounded-[7px] bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]">
                  <feature.icon className="size-5" />
                </span>
                <h3 className="mt-4 font-display text-lg font-bold text-[#07161d]">{feature.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-[var(--peer-muted)]">{feature.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="saudi-map" className="mx-auto max-w-7xl scroll-mt-16 px-4 py-16 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="peer-eyebrow">Saudi Arabia map</p>
            <h2 className="font-display mt-3 text-4xl font-bold text-[#07161d]">Discover success stories across Saudi Arabia</h2>
          </div>
          <p className="max-w-md text-sm text-[var(--peer-muted)]">The existing interactive Saudi map remains live and connected to the use-case data contract.</p>
        </div>
        <InteractiveMap height="600px" showTitle={false} className="overflow-hidden rounded-[7px] border border-[var(--peer-line)] bg-[var(--peer-surface)] shadow-[var(--peer-shadow)]" />
      </section>

      <section id="featured-use-cases" className="scroll-mt-16 bg-[var(--peer-surface)]">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mb-9 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <p className="peer-eyebrow">Featured factory solutions</p>
              <h2 className="font-display mt-3 text-4xl font-bold text-[#07161d]">Real implementations with measurable results</h2>
            </div>
            <Button onClick={() => navigate("/usecases")} variant="outline" className="rounded-[5px]">Open library<ArrowRight className="size-4" /></Button>
          </div>
          <div className="grid gap-5 lg:grid-cols-2">
            {featuredCases.map((item) => (
              <article key={item.title} className="peer-panel rounded-[7px] p-6">
                <div className="mb-5 flex items-center gap-3">
                  <span className="grid size-11 place-items-center rounded-[7px] bg-[var(--peer-navy)] text-white">
                    <item.icon className="size-5" />
                  </span>
                  <span className="rounded-full bg-[var(--peer-teal-soft)] px-3 py-1 text-xs font-bold text-[var(--peer-teal)]">{item.category}</span>
                </div>
                <h3 className="font-display text-2xl font-bold text-[#07161d]">{item.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-[var(--peer-muted)]">{item.body}</p>
                <div className="my-6 grid grid-cols-2 gap-4 border-y border-[var(--peer-line)] py-5">
                  <Metric value={item.primary} label={item.primaryLabel} />
                  <Metric value={item.secondary} label={item.secondaryLabel} />
                </div>
                <Button onClick={() => navigate(item.path)} variant="outline" className="w-full rounded-[5px]">View full case study</Button>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mb-9">
          <p className="peer-eyebrow">Factory success stories</p>
          <h2 className="font-display mt-3 text-4xl font-bold text-[#07161d]">Real results from Saudi manufacturing leaders</h2>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {stories.map((story) => (
            <article key={story.title} className="border-t-4 border-[var(--peer-teal)] bg-[var(--peer-surface)] p-6 shadow-[var(--peer-shadow)]">
              <story.icon className="size-5 text-[var(--peer-teal)]" />
              <h3 className="font-display mt-4 text-xl font-bold text-[#07161d]">{story.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-[var(--peer-muted)]">{story.desc}</p>
              <div className="mt-6 inline-flex rounded-[5px] bg-[var(--peer-navy)] px-4 py-2 text-sm font-bold text-white">{story.metric}</div>
            </article>
          ))}
        </div>
      </section>

      <section id="join-network" className="scroll-mt-16 bg-[var(--peer-navy)] py-16 text-white">
        <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
          <p className="peer-eyebrow text-[#9cb4b5]">Join the factory network</p>
          <h2 className="font-display mt-3 text-4xl font-bold sm:text-5xl">Connect with Saudi manufacturers and proven solutions.</h2>
          <p className="mx-auto mt-5 max-w-2xl text-[#c7d8d7]">
            Connect with factory owners across Saudi Arabia, browse proven use cases, and optimize your operations.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            {isAuthenticated && user ? (
              <>
                <div className="inline-flex items-center gap-3 rounded-[5px] bg-white/10 px-5 py-3 font-semibold text-white">
                  <User className="size-5" />Welcome back, {user.firstName} {user.lastName}
                </div>
                <Button onClick={() => navigate("/dashboard")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] px-6 text-white hover:bg-[#0f5ccc]">Go to dashboard<ArrowRight className="size-4" /></Button>
              </>
            ) : (
              <>
                <Button onClick={() => navigate("/signup")} className="h-12 rounded-[5px] bg-[var(--peer-blue)] px-6 text-white hover:bg-[#0f5ccc]">Get started free<ArrowRight className="size-4" /></Button>
                <Button onClick={() => navigate("/login")} variant="outline" className="h-12 rounded-[5px] border-white/30 bg-white/5 px-6 text-white hover:bg-white/10 hover:text-white">Sign in</Button>
              </>
            )}
          </div>
        </div>
      </section>

      <footer className="bg-[#07161d] py-12 text-white">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-4 text-center sm:px-6 md:flex-row md:text-left lg:px-8">
          <div>
            <div className="flex items-center justify-center gap-3 md:justify-start">
              <span className="grid size-10 place-items-center rounded-[5px] bg-[var(--peer-teal)]"><Factory className="size-5" /></span>
              <span className="font-display text-2xl font-bold">PeerLink</span>
            </div>
            <p className="mt-3 max-w-xl text-sm text-[#9cb4b5]">Factory optimization network connecting Saudi Arabian manufacturers with proven solutions and expert knowledge.</p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-[#9cb4b5]">
            <a href="#top" className="hover:text-white">Privacy</a>
            <a href="#top" className="hover:text-white">Terms</a>
            <a href="#top" className="hover:text-white">Support</a>
            <span className="inline-flex items-center gap-1"><MapPin className="size-4" />Saudi Arabia</span>
            <span>2026 PeerLink</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

function Metric({ value, label }: { value: ReactNode; label: string }) {
  return (
    <div>
      <div className="font-display text-2xl font-bold text-[var(--peer-teal)]">{value}</div>
      <div className="mt-1 text-xs text-[var(--peer-muted)]">{label}</div>
    </div>
  )
}

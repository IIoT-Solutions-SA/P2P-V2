import type { ReactNode } from "react"
import { AlertTriangle, Ban, Inbox, Loader2, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type AppStateProps = {
  title: string
  description?: ReactNode
  actionLabel?: string
  onAction?: () => void
  className?: string
}

function StateFrame({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className,
}: AppStateProps & { icon: ReactNode }) {
  return (
    <div className={cn("peer-panel flex min-h-[320px] flex-col items-center justify-center px-6 py-12 text-center", className)}>
      <div className="mb-5 grid size-12 place-items-center rounded-full bg-[var(--peer-teal-soft)] text-[var(--peer-teal)]">
        {icon}
      </div>
      <h2 className="font-display mb-2 text-xl font-semibold tracking-normal text-[var(--peer-ink)]">{title}</h2>
      {description ? <div className="max-w-md text-sm leading-6 text-[var(--peer-muted)]">{description}</div> : null}
      {actionLabel && onAction ? (
        <Button className="mt-6 bg-[var(--peer-teal)] text-white hover:bg-[var(--peer-navy-soft)]" onClick={onAction}>
          <RefreshCw className="size-4" />
          {actionLabel}
        </Button>
      ) : null}
    </div>
  )
}

export function LoadingState({ title = "Loading workspace", description, className }: Partial<AppStateProps>) {
  return (
    <StateFrame
      title={title}
      description={description}
      className={className}
      icon={<Loader2 className="size-5 animate-spin" aria-hidden="true" />}
    />
  )
}

export function EmptyState(props: AppStateProps) {
  return <StateFrame {...props} icon={<Inbox className="size-5" aria-hidden="true" />} />
}

export function ErrorState(props: AppStateProps) {
  return <StateFrame {...props} icon={<AlertTriangle className="size-5" aria-hidden="true" />} />
}

export function AccessDeniedState(props: AppStateProps) {
  return <StateFrame {...props} icon={<Ban className="size-5" aria-hidden="true" />} />
}


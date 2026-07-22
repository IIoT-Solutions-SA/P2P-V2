import type { LucideIcon } from "lucide-react"
import { BarChart3, BookOpen, Building2, Home, MessageSquare, Users } from "lucide-react"

export type AppNavItem = {
  label: string
  path: string
  icon: LucideIcon
  protected?: boolean
  group: "workspace" | "organization" | "public"
}

export const workspaceNavItems: AppNavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: BarChart3, protected: true, group: "workspace" },
  { label: "Forum", path: "/forum", icon: MessageSquare, protected: true, group: "workspace" },
  { label: "People", path: "/connect", icon: Users, protected: true, group: "workspace" },
  { label: "Use Cases", path: "/usecases", icon: BookOpen, protected: true, group: "workspace" },
]

export const organizationNavItems: AppNavItem[] = [
  { label: "Organization", path: "/organization", icon: Building2, protected: true, group: "organization" },
]

export const publicNavItems: AppNavItem[] = [
  { label: "Home", path: "/home", icon: Home, group: "public" },
  { label: "Use Cases", path: "/usecases", icon: BookOpen, protected: true, group: "public" },
  { label: "Forum", path: "/forum", icon: MessageSquare, protected: true, group: "public" },
]

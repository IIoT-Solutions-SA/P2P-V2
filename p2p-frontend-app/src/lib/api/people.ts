import { api } from "@/lib/api/client"

export interface OrganizationMember {
  id: string
  email: string
  firstName?: string
  lastName?: string
  name?: string
  role: "admin" | "member" | string
  title?: string
  company?: string
  location?: string
  industrySector?: string
  expertiseTags?: string[]
  isActive?: boolean
  createdAt?: string
  profilePictureUrl?: string
  isCurrentOrganization?: boolean
}

export const peopleApi = {
  directory: () => api.get<{ users: OrganizationMember[]; total: number }>("/api/v1/auth/users/directory"),
  organizationMembers: () => api.get<{ users: OrganizationMember[] }>("/api/v1/auth/users/organization"),
}
